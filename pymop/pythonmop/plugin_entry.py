from pythonmop.logicplugin.javamop import shutdownJVM
from pythonmop.mop_to_py import mop_to_py
from pythonmop.debug_utils import activate_debug_message
from pythonmop.debug_utils import PrintViolationSingleton
from pythonmop.statistics import StatisticsSingleton
from pythonmop.spec.data import End
import pythonmop.spec.spec as spec
from pythonmop.builtin_instrumentation import apply_instrumentation

import pytest
import importlib.util
from typing import List, Dict
import os
import time
import sys

# store reference to the original time function.
# this is used to avoid using a mocked implementation accidentally
original_time = time.time

# Global value indicating if the raw tests are running.
RAW_TESTS = False

# Global variable for tests time measurement.
TESTS_TIME = 0.0
TESTS_START_TIME = None

# Global variable to control curse instrumentation
_ENABLE_CURSE_INSTRUMENTATION = False

def is_curse_instrumentation_enabled():
    """Check if curse instrumentation is enabled.

    Returns:
        bool: True if curse instrumentation is enabled, False otherwise.
    """
    return _ENABLE_CURSE_INSTRUMENTATION


"""A python file containing pytest hooks for developing the pytest plugin.
"""

def inject_instrumentable_builtins(module):
    module.__dict__['list'] = ____pymop__injected__builtins____.list
    module.__dict__['dict'] = ____pymop__injected__builtins____.dict


def pytest_addoption(parser):
    """Define the arguments which is going to be taken by the pytest plugin.

        Args:
            parser: This is the parser defined by Pytest (not changeable).
    """

    # Take the spec folder filepath from the pytest arguments.
    parser.addoption(
        "--path", action="store", default=None, help="Path to the spec folder to be used"
    )

    # Take the spec names from the pytest arguments.
    parser.addoption(
        "--specs", action="store", default="all", help="The names of the specs to be checked (all for using all specs)"
    )

    # Take the algorithm name used from the pytest arguments.
    parser.addoption(
        "--algo", action="store", default=None, help="The name of the parametric algorithm to be used."
    )

    # Take the boolean value for printing out the info of the specs from the pytest arguments.
    parser.addoption(
        "--info", action="store_true", default=False, help="Print the descriptions of specs in the spec folder"
    )

    # Take the boolean value for printing out the debug messages for testing purposes.
    parser.addoption(
        "--debug_msg", action="store_true", default=False, help="Print the debug messages for testing purposes"
    )

    # Take the boolean value for printing out the detailed instrumentation messages.
    parser.addoption(
        "--detailed_msg", action="store_true", default=False, help="Print the detailed instrumentation messages"
    )

    # Take the boolean value for printing out the statistics of the monitor to the terminal.
    parser.addoption(
        "--statistics", action="store_true", default=False, help="Print the statistics of the monitor"
    )

    # Take the filepath for the statistics file from the pytest arguments.
    parser.addoption(
        "--statistics_file", action="store", default=None, help="The file to store the statistics of the monitor. It "
                                                                "can be either a json file or a txt file.  If not "
                                                                "provided, the statistics will be printed."
    )

    # Take the boolean value for printing out the spec violations during runtime.
    parser.addoption(
        "--noprint", action="store_true", default=False, help="When violations happens, no prints will be "
                                                              "shown in the terminal at runtime."
    )

    # Take the boolean value for refreshing the monitors' states during runtime.
    parser.addoption(
        "--refresh_monitors", action="store_true", default=False, help="Refresh the monitor states before each test. "
                                                                       "This can improve the performance."
    )

    # Take the boolean value for converting the front-end specs to the usable specs during the  setup stage.
    parser.addoption(
        "--convert_specs", action="store_true", default=False, help="Converting front-end specs to PyMOP internal "
                                                                    "specs for correct usages."
    )

    parser.addoption(
        "--instrument_pytest", action="store_true", default=False, help="Instrument the pytest plugin. It can be slow."
    )

    parser.addoption(
        "--instrument_pymop", action="store_true", default=False, help="Instrument the PyMOP library. It can be slow."
    )

    parser.addoption(
        "--no_garbage_collection", action="store_true", default=False, help="Perform garbage collection for the index tree."
    )

    parser.addoption(
        "--instrument_strategy", action="store", default="curse", help="Choose the instrumentation strategy to be used. The options are 'curse' or 'builtin'."
    )

def pytest_configure(config):
    """Apply the instrumentation and monitor creation before running the tests.

        Args:
            config: This is defined by Pytest (not known & changeable).
    """

    # Global value indicating if the raw tests are running.
    global RAW_TESTS

    # Global value indicating which instrumentation strategy to use.
    global _ENABLE_CURSE_INSTRUMENTATION

    # ==============================
    #  PLUGIN INITIAL MESSAGES PART
    # ==============================

    # Print out the welcome message.
    print(f"*** Welcome to use PythonMOP (Version 0.1.0)!")

    # Set builtin instrumentation flag
    instrument_strategy = config.getoption("instrument_strategy")
    if instrument_strategy == "builtin":
        print("Builtin type instrumentation is enabled.")
        apply_instrumentation(False)
    elif instrument_strategy == "ast":
        print("AST type instrumentation is enabled.")
        apply_instrumentation(True)
    elif instrument_strategy == "curse":
        _ENABLE_CURSE_INSTRUMENTATION = True
        print("Curse instrumentation is enabled.")
    else:
        print("Invalid instrumentation strategy. Please choose 'builtin' or 'curse'.")
        sys.exit(1)

    # Declare the names of the supported parametric algorithms
    supported_algo_names = ['A', 'B', 'C', 'C+', 'D']

    # Declare a list in config to store all the spec instances created.
    config.spec_instances = []

    # (Option) Print out the statistics of the monitor.
    if config.getoption("statistics"):
        StatisticsSingleton().set_full_statistics()

    # (Option) Set the file name for storing the statistics.
    if config.getoption("statistics_file"):
        file_name = config.getoption("statistics_file")
        StatisticsSingleton().set_file_name(file_name)
        print(f"The file name to store the statistics: {file_name}.")
    else:
        print("No file name is provided for storing the statistics. Statistics will be printed in this case.")

    # (Option) Instrument the pytest plugin.
    if config.getoption("instrument_pytest"):
        print("Instrumenting pytest plugin")
        spec.DONT_MONITOR_PYTEST = False
    # (Option) Instrument the PyMOP library.
    if config.getoption("instrument_pymop"):
        print("Instrumenting PyMOP library")
        spec.DONT_MONITOR_PYTHONMOP = False


    # Extract the algorithm name from the pytest arguments and print it out.
    algo_name = config.getoption("algo")
    if algo_name is None:
        print("No algorithm name is provided. Raw tests will be run in this case.")
        RAW_TESTS = True
        return  # Run raw tests and directly exit the function.
    elif algo_name not in supported_algo_names:
        print("The name of the algorithm is not supported. Raw tests will be run in this case.")
        RAW_TESTS = True
        return  # Run raw tests and directly exit the function.
    else:
        print(f"Parametric algorithm {algo_name} is currently being used.")

    # Extract the garbage collection option from the pytest arguments and print it out.
    garbage_collection_flag = not config.getoption("no_garbage_collection")
    if garbage_collection_flag:
        print("Garbage collection is currently being used.")
    else:
        print("Garbage collection is not being used.")

    # Extract the spec folder path from the pytest arguments and print it out.
    folder_path = config.getoption("path")
    if folder_path is None:
        print("No path to the spec folder is provided. Raw tests will be run in this case.")
        return  # Run raw tests and directly exit the function.
    else:
        print(f"The path to the spec folder: {folder_path}.")

    if config.getoption("convert_specs"):
        results = _spec_converting(folder_path)
        if results:
           print(f"The new specs converted: {results}.")
        else:
            print("No new specs were converted.")

    # Extract the spec names from the pytest arguments.
    specs_string = config.getoption("specs")

    # Find the spec names used in the test run from the spec string.
    if specs_string != "all":
        spec_names = specs_string.strip().split(',')
    else:
        spec_names = _spec_names_extracting(folder_path, config.getoption("instrument_strategy"))

    # (Option) Print out the description fo the spec without doing any instrumentation and tests.
    if config.getoption("info"):
        # Import the spec classes and print out the descriptions.
        spec_classes = _spec_classes_importing(folder_path, spec_names, False, config.getoption("instrument_strategy"))
        _spec_info_printing(spec_classes)

        # Force the pytest to exit without running tests.
        pytest.exit("Pytest exiting after printing descriptions.")

    # (Option) Print out the debug messages of the tool for testing purposes.
    if config.getoption("debug_msg"):
        # Change the boolean value for debug messages into True.
        activate_debug_message()

    # (Option) Not print out the spec violations during runtime.
    if config.getoption("noprint"):
        print("No prints will be shown in the terminal when violations happen at runtime.")
        PrintViolationSingleton().deactivate_print_output_violation()

    if config.getoption("refresh_monitors"):
        print("Refresh the monitor states before each test.")
    else:
        print("No refresh for the monitor states before each test.")

    # Print out the number of specs and spec names used in the test run.
    print(f"{len(spec_names)} specs are found for the current test run.")
    print(f"The specs found for the current test run: {spec_names}.")

    # =============================
    #  SPEC CLASSES IMPORTING PART
    # =============================

    # Get the detailed message option.
    detailed_message = config.getoption("detailed_msg")

    # Start timing the specs instrumentation.
    instrumentation_start_time = original_time()

    # Extract the spec classes from the spec files in the spec folder.
    spec_classes = _spec_classes_importing(folder_path, spec_names, detailed_message, config.getoption("instrument_strategy"))

    # End timing the specs instrumentation.
    instrumentation_end_time = original_time()
    instrumentation_duration = instrumentation_end_time - instrumentation_start_time
    StatisticsSingleton().add_instrumentation_duration(instrumentation_duration)

    # Print out the number of importable specs and spec names used in the test run.
    print(f"{len(spec_classes)} specs are usable for the current test run.")
    print(f"The specs useful for the current test run: {spec_classes.keys()}.")

    # ============================
    #  SPECS INSTRUMENTATION PART
    # ============================

    # Print out the debug message before doing the instrumentation.
    if detailed_message:
        print("============================ Instrumentation starts ============================")

    # Start timing the specs instrumentation.
    create_monitor_start_time = original_time()

    # Apply the instrumentation and create the monitor with the debug message printed out if the detailed_msg is True.
    for spec_name in spec_classes.keys():
        if detailed_message:
            print(f"* Instrumenting Spec {spec_name}:")
        spec_instance = spec_classes[spec_name]()
        spec_instance.create_monitor(algo_name, detailed_message, garbage_collection_flag)

        # if algo is A
        if algo_name == 'A':
            m = spec_instance.get_monitor()
            if m is not None:
                m.clear_trace_file()

        # Add the spec instance into the list in config.
        config.spec_instances.append(spec_instance)

    # End timing the specs instrumentation.
    create_monitor_end_time = original_time()
    create_monitor_duration = create_monitor_end_time - create_monitor_start_time
    StatisticsSingleton().add_create_monitor_duration(create_monitor_duration)

    # Terminate JVM used for formula parsing
    shutdownJVM()


def _spec_converting(folder_path):

    results = []

    # Check through each file and add the spec name into the list.
    for spec_name in os.listdir(folder_path):
        if spec_name.endswith(".mop"):
            mop_to_py(folder_path, spec_name[:-4])
            results.append(spec_name[:-4])

    return results

def _spec_info_printing(spec_classes: Dict[str, callable]) -> None:
    """Print the descriptions of the specs defined by the users.

        Args:
            spec_classes: one Dict containing all the spec names and classes.
    """

    # Print out the debug message before printing the descriptions.
    print("============================== Specs descriptions ==============================")

    # Print the description of each spec.
    for spec_name in spec_classes.keys():
        print(f"{spec_name}: {spec_classes[spec_name].__doc__}")


def _spec_names_extracting(folder_path: str, strategy) -> List[str]:
    """Find all the spec names in the spec folder provided.

        Args:
            folder_path: The path to the folder where the specs are stored.
        Returns:
            One list containing all the spec names in the folder for future uses.
    """

    specs_to_ignore_with_curse = [
        'UnsafeMapIterator',
        'UnsafeListIterator',
        'PyDocs_MustSortBeforeGroupBy',
        'Arrays_SortBeforeBinarySearch'
    ]

    # Declare one variable for storing the spec name extracted.
    spec_names = []

    # Check through each file and add the spec name into the list.
    for spec_name in os.listdir(folder_path):
        if spec_name.endswith(".py"):
            name = spec_name[:-3]
            if strategy == 'curse' and name in specs_to_ignore_with_curse:
                continue

            spec_names.append(name)  # remove .py extension

    # Return all the spec names extracted.
    return spec_names


def _spec_classes_importing(folder_path: str, spec_names: List[str], detailed_message: bool, strategy) -> Dict[str, callable]:
    """Import the spec classes from the spec files defined by the users.

        Args:
            folder_path: The path to the folder where the specs are stored.
            spec_names: The name of the specs to be used in the test run.
            detailed_message: The boolean value for printing out the detailed instrumentation messages.
        Returns:
            One Dict containing all the spec classes extracted for future uses.
    """

    # Print out the debug message before doing the specs import.
    if detailed_message:
        print("=============================== Importing starts ===============================")

    # Declare one variable for storing the spec classes imported.
    spec_classes = {}

    # Import each spec class from the files.
    for spec_name in spec_names:

        # Form the path to the spec file using the spec name.
        spec_path = folder_path + '/' + spec_name + '.py'

        # Get the class attribution for the spec file.
        # If an ModuleNotFoundError is returned, then skip the current spec
        try:
            spec = importlib.util.spec_from_file_location(spec_name, spec_path)
            spec_module = importlib.util.module_from_spec(spec)
            if strategy == 'ast':
                try:
                    inject_instrumentable_builtins(spec_module)
                except Exception as e:
                    print('Failed to inject instrumentable builtins. if you are running AST instrumentation, please make sure to make PYTHONPATH point to the pythonmop/pymop-startup-helper folder')
            spec.loader.exec_module(spec_module)
            spec_class = getattr(spec_module, spec_name, None)

            # Add the module's directory to sys.path
            module_dir = os.path.dirname(spec_path)
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)

            # Print out the result of importing the spec class.
            if spec_class is not None:
                if detailed_message:
                    print(
                        f"* Successfully imported spec class '{spec_name}' from '{spec_path}'")

                # Add the class attribution into the dict.
                spec_classes[spec_name] = spec_class
            else:
                print(
                    f"* ERROR: Cannot find spec class '{spec_name}' in '{spec_path}'")

        # Handle the ModuleNotFoundError exception by printing out an skipping message
        except ModuleNotFoundError as e:
            print(
                f"* SKIPPED: Missing dependency while importing '{spec_name}' from '{spec_path}'.")

    # Return all the spec classes imported.
    return spec_classes


def _spec_instance_storing(spec_instance, spec_instances_fixture):
    """Add the spec instance to the spec_instance list in config for future uses.

        Args:
            spec_instance: The spec instance to be added.
            spec_instances_fixture: The fixture list which contains the spec instances.
    """

    spec_instances_fixture.append(spec_instance)


def _refresh_monitor_states(spec_instances):
    # Refresh each spec monitor for the next test.
    for spec_instance in spec_instances:
        monitor = spec_instance.get_monitor()
        if monitor is not None:
            monitor.refresh_monitor()


def pytest_runtest_setup(item):
    """Refresh the monitor states before each test.

        Args:
            item: The pytest item being tested.
    """

    # mark the start time
    global TESTS_START_TIME
    if (TESTS_START_TIME == None):
        TESTS_START_TIME = original_time()
        print('Saving the start time at: ', TESTS_START_TIME)

    # Get all the spec instances that are currently using.
    spec_instances = item.config.spec_instances
    if item.config.getoption("refresh_monitors"):
        _refresh_monitor_states(spec_instances)


def pytest_runtest_teardown(item):
    """Summary the statistics for each spec monitor after each test.

        Args:
            item: The pytest item being tested.
    """

    # Get all the spec instances that are currently using.
    spec_instances = item.config.spec_instances

    # Summary the statistics for each spec monitor.
    for spec_instance in spec_instances:
        spec_instance.end()

    global TESTS_START_TIME
    global TESTS_TIME
    if (TESTS_START_TIME == None):
        print('ERROR: Could not find TESTS_START_TIME. this means pytest_runtest_teardown was called before pytest_runtest_setup')

    end_time = original_time()
    test_duration = end_time - TESTS_START_TIME
    TESTS_TIME = test_duration

    # print(f'INFO: Updated the test duration. end_time {end_time} - start_time {TESTS_START_TIME} = duration {TESTS_TIME}')


def pytest_sessionfinish(session, exitstatus):
    """Print out the statistics of the monitor after running the tests.
        Args:
            session: This is defined by Pytest (not known & changeable).
            exitstatus: This is defined by Pytest (not known & changeable).
    """

    # Print out the debug message before printing the statistics.
    global RAW_TESTS
    global TESTS_TIME

    # call the end_execution help function to end the execution of the program.
    End().end_execution()

    # Refresh the monitor states for the last time.
    if session.config.getoption("algo") == 'A':
        _refresh_monitor_states(session.config.spec_instances)

    print("============================ PythonMOP Statistics starts ============================")
    # Print out the statistics of the monitor.
    StatisticsSingleton().add_test_duration(TESTS_TIME)

    if RAW_TESTS:
        StatisticsSingleton().print_raw_statistics()
    else:
        StatisticsSingleton().print_statistics()


def pytest_runtest_protocol(item, nextitem):
    """
    This hook is called before and after the execution of each test.
    'item' is the current test item, and 'nextitem' is the next test item in the queue.

    You can access information about the test using the 'item' object.
    """
    # test_location = item.location
    test_name = item.nodeid

    # if algo is A, don't set the current test name
    # as the algo will run after all the tests run
    # it will point to the last test
    if item.config.getoption("algo") == 'A':
        test_name = ""

    StatisticsSingleton().set_current_test(test_name)

    # Do something with the test information if needed

    # Returning None means to proceed with the normal test execution flow
    return None
