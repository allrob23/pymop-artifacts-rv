import pytest
import os
import importlib.util
import itertools
import subprocess
import uuid
import json

SPECS_DIR = "./specs-new"
TESTS_DIR = "tests/e2e/spec-tests"

ALGOS = ['A', 'B', 'C', 'C+', 'D']  # Ensure this list matches the length of spec_names

def get_absolute_path(relative_path):
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Join the directory with the relative path to get the absolute path
    absolute_path = os.path.join(current_directory, relative_path)

    # Normalize the path to remove any redundant separators or up-level references
    absolute_path = os.path.normpath(absolute_path)

    return absolute_path


@pytest.fixture(scope="session", autouse=True)
def clear_traces():
    # before running the first test, remove all files in the format "trace_*.txt in actual dir"
    # after running all tests, printout the summary and saves in a file
    count = 1
    p = get_absolute_path('../../')
    for file in os.listdir(p):
        if file.startswith('trace_') and file.endswith('.txt'):
            os.remove(f'{file}')
            count += 1
    print(f"\nRemoved {count} trace files before running tests\n")
    yield
    # after running all tests, printout the summary and saves in a file
    print('//////////////////////////////////////')
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
    print('//////////////////////////////////////')
    print('Summary')
    print('//////////////////////////////////////')
    print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
    print('//////////////////////////////////////')
    # sort the keys of the summary
    s = dict(sorted(summary.items()))
    print(json.dumps(s, indent=2))
    # save in a file
    with open('summary.json', 'w') as f:
        json.dump(s, f, indent=2)
    print('summary saved in summary.json')

    # print the complete summary
    # sort the keys of the summary
    s_complete = dict(sorted(summary_complete.items()))
    print("\nsummary_complete:")
    print(json.dumps(s_complete, indent=2))
    # save in a file
    with open('summary_complete.json', 'w') as f:
        json.dump(s_complete, f, indent=2)

# List all files in the directory
files = os.listdir(SPECS_DIR)

# Filter for .py files and get filenames without the extension
spec_names = [os.path.splitext(file)[0] for file in files if file.endswith(".py")]

# Skip specs that are known to be ok but are problematic in the ci.
skip_specs = [
    "Turtle_LastStatementDone",
    "Console_CloseWriter", # it closes the stdout so we can't run this one
    "Two_Classes_Binding",
    'Pydocs_ShouldUseStreamWriterCorrectly', # show unexpected results in the ci. Algo A is flaky locally, but flakiness is likely caused by the e2e tests themselves rather than pymop implementation.
]
spec_names = [spec for spec in spec_names if spec not in skip_specs]
expected_violations = {}

# Function to load a module from a file
def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Iterate over each .py file, load it, and read the contents of the 'violations' array
for file in spec_names:
    file_path = os.path.join(TESTS_DIR, file + "_test.py")

    try:
        module = load_module_from_file(file, file_path)
    except Exception as e:
        print(f"Error loading module {file}: {e}")
        expected_violations[file] = None
        continue

    for algo in ['A', 'B', 'C', 'C_plus', 'D']:
        if not hasattr(module, f"expected_violations_{algo}"):
            raise Exception(f"Expected '{f'expected_violations_{algo}'}' attribute in {file_path}")

    def get_func_names(expected_violations_list):
        return [violation.__name__ for violation in expected_violations_list]
    
    # A should be an integer
    if not isinstance(getattr(module, "expected_violations_A"), int):
        raise Exception(f"Expected 'expected_violations_A' attribute in {file}.py is not an integer")

    # Other algos should be lists
    for algo in ['B', 'C', 'C_plus', 'D']:
        if not isinstance(getattr(module, f"expected_violations_{algo}"), list):
            raise Exception(f"Expected 'expected_violations_{algo}' attribute in {file}.py is not a list")

    # All elements in the lists should be functions
    for algo in ['B', 'C', 'C_plus', 'D']:
        for violation in getattr(module, f"expected_violations_{algo}"):
            # should be a function
            if not callable(violation):
                raise Exception(f"Some of the expected violations for algo {algo} in {file}.py are not functions")

    expected_violations[file] = {
        "A": getattr(module, "expected_violations_A"),
        "B": get_func_names(getattr(module, "expected_violations_B")),
        "C": get_func_names(getattr(module, "expected_violations_C")),
        "C+": get_func_names(getattr(module, "expected_violations_C_plus")),
        "D": get_func_names(getattr(module, "expected_violations_D"))
    }

print('========================================')
print('========================================')
print('========================================')

# Generate all combinations of algos and spec names
combinations = list(itertools.product(ALGOS, spec_names))
combinations_with_index = [(index, algo, spec) for index, (algo, spec) in enumerate(combinations)]

# Generate the array of tuples with the algorithm, spec name, and violation function names
testdata = [(index, algo, spec, False if expected_violations[spec] is not None else True, expected_violations[spec][algo] if expected_violations[spec] is not None else []) for index, algo, spec in combinations_with_index]

summary = {}
summary_complete = {}

@pytest.mark.parametrize("index,algo,spec_name,should_skip,expected_violations", testdata)
def test_timedistance_v0(index, algo, spec_name, should_skip, expected_violations):
    print('\n\n\n========================================')
    print(f'({index+1}/{len(testdata)}) Testing {spec_name} with {algo}')
    if should_skip:
        print(f'Skipping {spec_name} with {algo}')
        pytest.skip()
    print('========================================')
    # add summary
    if spec_name not in summary:
        summary[spec_name] = {}
    summary[spec_name][algo] = "STARTED"

    if spec_name not in summary_complete:
        summary_complete[spec_name] = {}
    if algo not in summary_complete[spec_name]:
        summary_complete[spec_name][algo] = {}
        summary_complete[spec_name][algo]['status'] = "STARTED"

    # run pymop on the spec
    test_path = get_absolute_path(f'./spec-tests/{spec_name}_test.py')
    specs_dir = get_absolute_path(f'../../specs-new')
    os.makedirs(get_absolute_path('../../temp/'), exist_ok=True)
    statistics_file = get_absolute_path(f'../../temp/{algo}-{str(uuid.uuid4()).replace("-", "_")}')
    # AST
    command = f'PYTHONPATH=./pythonmop/pymop-startup-helper pytest -s {test_path} -p pythonmop --path={specs_dir} --algo {algo} --statistics --statistics_file={statistics_file}.json --specs={spec_name} --instrument_pymop --instrument_pytest --instrument_strategy ast'
    # CURSES
    # command = f'pytest -s {test_path} -p pythonmop --path={specs_dir} --algo {algo} --statistics --statistics_file={statistics_file}.json --specs={spec_name} --instrument_pymop --instrument_pytest --instrument_strategy curse'
    # MONKEY PATCHING
    # command = f'pytest -s {test_path} -p pythonmop --path={specs_dir} --algo {algo} --statistics --statistics_file={statistics_file}.json --specs={spec_name} --instrument_pymop --instrument_pytest --instrument_strategy builtin'

    print('Running command:\n', command, '\n')
    tests_result = None
    try:
        tests_result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        summary_complete[spec_name][algo]['output'] = tests_result.stdout

    except subprocess.CalledProcessError as e:
        # # Handle errors in the called process
        print('\n\n========================================')
        print(f"could not run algo {algo} on spec {spec_name}.")
        print(f"Command: {command}")
        print(f"Output: {e.output}")
        print('========================================')
        print('\n\n')

        summary[spec_name][algo] = "FAILED"
        summary_complete[spec_name][algo]['status'] = "FAILED"
        summary_complete[spec_name][algo]['error'] = e.output

        # assert False, f"could not run algo {algo} on spec {spec_name}. Original error {e.output}"

    # read the data from {statistics_file}-violations.json
    violations_file = f'{statistics_file}-violations.json'

    try:
        with open(violations_file, 'r') as f:
            # parse the violations json
            violations = json.load(f)

            '''
            The format of the violations json file is:
            {
                [spec_name]: [
                    {
                        "violation": "violation path etc",
                        "test": "violation name"
                    }
                ]
            }
            '''
    except Exception as e:
        if summary[spec_name][algo] != "FAILED":
            print(f"Error loading violations file {violations_file}: {e}")
            summary[spec_name][algo] = "FAILED"
            summary_complete[spec_name][algo]['error'] = e
            summary_complete[spec_name][algo]['status'] = "FAILED"
        
        assert False, f"could not run algo {algo} on spec {spec_name}. Original error {summary_complete[spec_name][algo]['error']}"

    # get all violations of the spec name
    violations = violations.get(spec_name, [])

    # in algo A, we use the number of violations
    found_num_violations_count = len(violations)
    
    summary[spec_name][algo] = "OK"
    summary_complete[spec_name][algo]['status'] = "OK"
    # in algo A, we use the number of violations
    if algo == 'A':
        summary_complete[spec_name][algo]['violations_found'] = found_num_violations_count
        summary_complete[spec_name][algo]['violations_expected'] = expected_violations

        if found_num_violations_count != expected_violations:
            summary[spec_name][algo] = "FAILED"
            summary_complete[spec_name][algo]['status'] = "FAILED"

        assert found_num_violations_count == expected_violations, f"Algo A: Expected {expected_violations} violations, but found {found_num_violations_count}"
    # in other algos, we use the names of the tests
    else:
        found_violation_names_sorted = sorted([violation['test'].split('::')[-1] for violation in violations])
        expected_violation_names_sorted = sorted(expected_violations)
        summary_complete[spec_name][algo]['violations_found'] = found_violation_names_sorted
        summary_complete[spec_name][algo]['violations_expected'] = expected_violation_names_sorted

        if found_violation_names_sorted != expected_violation_names_sorted:                
            summary[spec_name][algo] = "FAILED"
            summary_complete[spec_name][algo]['status'] = "FAILED"

        assert found_violation_names_sorted == expected_violation_names_sorted, f"Algo {algo}: Expected violations {expected_violation_names_sorted}, but found {found_violation_names_sorted}"

