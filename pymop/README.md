# PyMOP

A Pytest plugin that implements MOP-style Runtime Verification (RV) for Python projects.

## System Requirements

PyMOP requires the following components to be installed on your system:

- **Python**: Version 3.12 or later
- **Java**: Version 20 or later
- **Docker**: (optional, but recommended for simplified setup)

## Tutorial

This tutorial demonstrates how to use PyMOP to perform runtime verification on an open-source Python project using Ubuntu Linux. The tutorial walks through installation, setup, and running PyMOP on a real-world example.

### Setup PyMOP with Docker

This is the recommended way to setup PyMOP as it is the easiest way to get started and avoid any dependency issues.

If you don't have Docker installed, follow the instructions [here](https://docs.docker.com/get-docker/) to install Docker.

There is currently one way to run PyMOP with Docker:

1. Building the Docker image from source

   a. Navigate to the `docker_files/demo` folder from the root directory:

   ```bash
   cd docker_files/demo
   ```

   b. Build the Docker image using:

   ```bash
   docker build -t pymop .
   ```

   This will build the Docker image and tag it as `pymop`.

   c. Run the Docker container using:

   ```bash
   docker run -it pymop
   ```

   This will start the Docker container and should include the PyMOP repository and all the dependencies.

   d. Activate the PyMOP virtual environment:

   The PyMOP docker image should have already install PyMOP in the `pymop-venv` virtual environment. You can activate it by running:

   ```bash
   source pymop-venv/bin/activate
   ```

   This will activate the PyMOP virtual environment and you can now use PyMOP on any project you want.

### Run PyMOP on a open-source project

This section will guide you through running PyMOP on a open-source project. We'll use the `gdipak` project as an example.

To run PyMOP on a open-source project, you need to follow these steps:

1. Set Up Test Project
   ```bash
   # Clone the test project (gdipak)
   git clone https://github.com/2pair/gdipak
   
   # Install project dependencies
   cd gdipak
   pip install .
   ```

2. Run PyMOP with the `gdipak` project using all the specifications in the `pymop-artifacts-rv/pymop/specs-new` folder.

   You can run PyMOP using one of the following commands:

   a. Run with **monkey patching + curse** instrumentation strategy **(recommended)**:
   ```bash
   pytest tests --algo=D --path="$PWD/../pymop-artifacts-rv/pymop/specs-new"
   ```

   b. Run with **monkey patching** instrumentation strategy:
   ```bash
   pytest tests --algo=D --path="$PWD/../pymop-artifacts-rv/pymop/specs-new" --instrument_strategy=builtin
   ```

   c. Run with **monkey patching + AST** instrumentation strategy:
   ```bash
   PYTHONPATH="$PWD/../pymop-artifacts-rv/pymop/pythonmop/pymop-startup-helper" pytest tests --algo=D --path="$PWD/../pymop-artifacts-rv/pymop/specs-new" --instrument_strategy=ast
   ```

   > **Note:** The **monkey patching + curse** strategy (default) is recommended for most cases as it provides the best balance of performance and reliability.

3. Violation Fixing (if applicable)

If the `PyMOP` finds violations, you can find the code place that violates the specification in the testing report printed out in the terminal.

### Re-run the runtime verification tests with the fixed code

After fixing the code, you can re-run the tests using the same command from Step 2 (e.g., `pytest tests --algo=D --path="$PWD/../pymop-artifacts-rv/pymop/specs-new"` for the recommended strategy).

## Installation

There are two ways to install PyMOP: using Docker (recommended) or installing directly on your system.

### Option 1: Docker Installation (Recommended)

The easiest way to get started with PyMOP is using Docker, which ensures all dependencies are properly set up (as described in the tutorial above):

1. Install Docker following the [official instructions](https://docs.docker.com/get-docker/)
2. Build the PyMOP Docker image:
   ```bash
   cd docker_files/demo
   docker build -t pymop .
   ```
3. Run the container:
   ```bash
   docker run -it pymop
   ```
4. Activate the virtual environment inside the container:
   ```bash
   source pymop-venv/bin/activate
   ```

### Option 2: Direct Installation

If you prefer to install PyMOP directly on your system, follow these steps:

1. The following dependencies are required to run PyMOP on your local system:
   * python3-tk
   * python3-venv

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv pymop-venv
   source pymop-venv/bin/activate  # On Unix/macOS
   # or
   .\pymop-venv\Scripts\activate  # On Windows
   ```

3. Clone and install PyMOP:
   ```bash
   git clone https://github.com/allrob23/pymop-artifacts-rv.git
   cd pymop-artifacts-rv/pymop
   pip install .
   ```

## Usage

After installation, the plugin will be automatically available when you run pytest on open-source projects.

## Command-line Options

The plugin provides multiple command-line options that allow you to customize how PyMOP is used:

### Command-line option 1:

`--path`: Specifies the path to the folder containing the specifications.

```bash
pytest tests --path=PATH
```

Replace `PATH` with the path to the folder containing the specifications you want to use.

DEFAULT: When no path is provided, the plugin will run the tests without performing any runtime verifications.

### Command-line option 2:

`--specs`: Specifies which specifications to use in the test run.

```bash
pytest tests --specs=SPEC1,SPEC2
```

Replace `SPEC1`, `SPEC2`... with the names of the specifications you want to use.

DEFAULT: When no specifications are specified, all specifications in the folder will be used.

### Command-line option 3:

`--algo`: Specifies the parametric algorithm PyMOP uses during the test run.

```bash
pytest tests --algo=D
```

Five algorithms are available: `A`, `B`, `C`, `C+`, and `D`. Algorithm `D` is the default algorithm and represents the most complex and comprehensive implementation in PyMOP. You can experiment with other algorithms, though note that there may be performance differences as discussed in our paper.

### Command-line option 4:

`--instrument_strategy`: Specifies the instrumentation strategy PyMOP uses during the test run.

```bash
pytest tests --instrument_strategy=curse
```

Three options are available: `builtin`, `curse`, and `ast`. Each instrumentation strategy has different benefits and trade-offs. Choose the one that best suits your needs (`curse` is used by default).

> **Note:** When using the `ast` strategy, you must add `PYTHONPATH="PATH TO pymop-artifacts-rv"/pymop/pythonmop/pymop-startup-helper` at the beginning of your pytest command.

### Command-line option 5:

`--statistics`: Prints statistics of the runtime verification results.

```bash
pytest tests --statistics
```

When using the `--statistics` option, the plugin will print statistics about the runtime verification results, including monitors created and events triggered.

DEFAULT: When the `--statistics` option is not used, tests will run normally without printing monitor statistics.

### Command-line option 6:

`--statistics_file`: Specifies the path to a JSON or text file where the runtime verification statistics will be stored.

```bash
pytest tests --statistics_file=PATH
```

DEFAULT: When the `--statistics_file` option is not provided, the monitor statistics will be printed to the terminal.
