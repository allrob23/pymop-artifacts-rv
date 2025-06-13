import importlib
import os


SPECS_DIR = "./specs-new"
TESTS_DIR = "tests/e2e/spec-tests"

# List all files in the directory
files = os.listdir(SPECS_DIR)

# Filter for .py files and get filenames without the extension
spec_names = set([os.path.splitext(file)[0] for file in files if file.endswith(".py")])
seen_specs = set()

# Iterate over each .py file, load it, and read the contents of the 'violations' array
for spec_name in spec_names:
    file_path = os.path.join(TESTS_DIR, spec_name + "_test.py")

    if os.path.exists(file_path):
        seen_specs.add(spec_name)

missing_specs = spec_names - seen_specs


if len(missing_specs) > 0:
    print(f"Missing e2e test for {missing_specs}")
    exit(1)
