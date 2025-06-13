# PythonMOP

One Pytest plugin that runs a MOP-style RV tool in Python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install PythonMOP.

### Option 1: Install via pip from PyPI (Not Available For Now)

You can install `pytest-pythonmop` directly from the Python Package Index using pip. This is the easiest method and will always give you the latest released version of `pytest-pythonmop`:

```bash
pip install pytest-pythonmop
```

### Option 2: Install from the Source Distribution

Alternatively, you can install `pytest-pythonmop` from the source distribution. This might be necessary if you want to make modifications to `pytest-pythonmop`:

```bash
pip install pytest-pythonmop-0.1.0.tar.gz
```

Please replace `pytest-pythonmop-0.1.0.tar.gz` with the path to the actual file if it is not in your current directory.

## Usage

After installation, the plugin will automatically be available when you run pytest. Below is an example of how to run PyMOP with an open-source project.

### Create a test folder and set up a Python virtual environment for this experiment
```bash
1. mkdir experiment
2. cd experiment
3. python -m venv env
4. source env/bin/activate
```

### Download and install PyMOP in the test folder
```bash
5. git clone --depth=1 https://github.com/SoftEngResearch/mop-with-dynapt
6. cd mop-with-dynapt
7. pip install .
8. rm specs-new/TfFunction_NoSideEffect.py  # This spec has some issues, so we remove it.
9. cd ..
```

### Download and install the testing open-source project (Textualize/rich in this case) in the test folder
```bash
10. git clone --depth=1 https://github.com/Textualize/rich
11. cd rich
12. pip install .
13. pip install attr  # This dependency is required but missing for some reason.
```

### Run the tests with PyMOP
```bash
14. pytest -rA tests --algo=D --path="$PWD"/../mop-with-dynapt/specs-new/ --statistics --statistics_file=D.json
```

- `--path` = the folder containing the specs
- `--algo` = the algorithm used to check violations
- `--statistics` and `--statistics_file` = create JSON files with statistical checks

When finished, you can see the print in the test output of the violation cases. In addition, 3 files are created with all the information:
`D-full.json` `D-time.json` and `D-violations.json`


## Command-line Options

The plugin provides six command-line options that allows you to specify the way you want to the plugin to be used:

### Command-line option 1:

--path: Specifies the path to the folder where the specs are stored.

```bash
pytest tests --path=PATH
```

Replace `PATH` with the path to the folder of the specs you want to use.

DEFAULT: When no path is provided, the plugin will run the raw tests without doing any verifications.

### Command-line option 2:

--specs: Specifies the specific specs to be used in the test run.

```bash
pytest tests --specs=SPEC1,SPEC2
```

Replace `SPEC1`, `SPEC2`... with the name of the specs you want to use.

EXTRA: Replace `SPEC1,SPEC2` with `all` if you want to use all the specs in the folder.

DEFAULT: When no specs are provided, `all` will be used as default.

### Command-line option 3:

--statistics: Prints out the statistics of runtime verification results.

```bash
pytest tests --statistics
```

When using `--statistics` option, the statistics of runtime verification results including monitors created and events triggered will be printed out.

DEFAULT: When `--statistics` option is not used, tests will be run by Pytest as normal and no monitor statistics will be printed out.

### Command-line option 4:

--statistics_file: Replace `PATH` with the path of a JSON or txt file that you want to store the statistics of runtime verification results.

```bash
pytest tests --statistics_file=PATH
```

DEFAULT: When `--statistics_file` option is not provided, the monitor statistics will be printed out through the terminal.

### Command-line option 5:

--noprint: Not print out the violation information during tests runtime.

```bash
pytest tests --noprint
```

When using `--noprint` option, the descriptions of the violations will not be printed out during runtime. However, a summary of the violations will still be printed at the end of the test run.

DEFAULT: When `--noprint` option is not used, the violation information will be printed during runtime.

### Command-line option 6:

--info: Prints out the descriptions of the existing specs defined by the users.

```bash
pytest tests --info
```

When using `--info` option, the descriptions of the specs will be printed out (No test will be run in this case).

DEFAULT: When `--info` option is not used, tests will be run by Pytest as normal.

### Extra helps:
You can see all command-line options provided by the plugin by running:

```bash
pytest --help
```

## Testing examples

There are runnable testing examples in the repository. Please refer to [TESTING.md](examples/TESTING.md)

## Internal Development and Testing Guidelines

If you're a member of the development team, please see the [CONTRIBUTING.md](CONTRIBUTING.md) for further development and test guidelines.

Note: These guidelines are intended for internal use by the development team. They are not meant for external contributors.
