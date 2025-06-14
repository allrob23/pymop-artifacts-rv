# A Generic and Efficient Python Runtime Verification System and its Large-scale Evaluation

## Appendix

The appendix is available [here](appendix.pdf). It contains:
* A detailed comparison of instrumentation strategies (discussed in Section 3)
* Our submitted PRs and issues (both accepted and rejected) from RQ3

## Projects and data

This repository contains the following data at locations in the following hyperlinks:

* [List of projects used in all RQs (including their GitHub URLs and commit SHAs)](Experiment_Data/projects_evaluated.csv)
* [Experiment data for RQ1: Comparison of PyMOP Online Algorithms](Experiment_Data/RQ1%20-%20Algorithms%20Comparison/)
* [Experiment data for RQ2: Comparison of PyMOP Instrumentation Strategies](Experiment_Data/RQ2%20-%20Instrumentation%20Strategies%20Comparison/)
* [Experiment data for RQ4: Comparison of DynaPyt, Dylin, and PyMOP](Experiment_Data/RQ4%20-%20Dynapyt_DyLin_PyMOP%20Comparison/)

## Repository structure

| Directory / File   | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| appendix.pdf       | Contains detailed supplementary information discussed in the paper |
| Docker             | Contains multiple Dockerfiles that can be built to run all RQ experiments |
| Experiment_Data    | Contains project information and experiment data for all RQs |
| pymop              | Contains the source code of PyMOP                            |
| scripts            | Contains the scripts to run all RQ experiments and parse the results |

## Usage

### Prerequisites

* An x86-64 architecture machine
* Ubuntu 22.04
* [Docker](https://docs.docker.com/get-docker/)

### RQ2: Comparison of PyMOP Instrumentation Strategies

#### Setup

First, you need to build a Docker image (this might take a short period of time). Please run the following command in your terminal:

```bash
docker build -t pymop-rq2 -f Docker/rq2/Dockerfile .
```

#### Run experiment

Execute the following command to start one Docker instance while mounting the `workspace` folder (in the Docker container) to the same folder locally:

```bash
docker run -it --rm -v $PWD/workspace:/workspace pymop-rq2
```

Copy all the experiment scripts from the `experiment` folder into the `workspace` folder for future usage:

```bash
cd ..
cp -r /experiment/* /workspace/
cd workspace/
```

The following command will execute the RQ2 experiment with the full project list. **Note: This experiment might take days to finish.** (If you want to test out PyMOP and the experiment, please reduce the number of projects in `projects_evaluated.csv`.)

```bash
./run_experiment_rq2.sh
```

#### Results

After you finish executing the command for a list of projects, all the results will be saved as zip files in the `workspace` folder.

Copy all the zip files into a separate folder (for example, a folder named "unzipped"). Place the [unzip_file.py](scripts/unzip_file.py) script into that folder and execute it (this will unzip all the results into a new folder). Then, place the [rq2_csv_parser.py](scripts/rq2_scripts/rq2_csv_parser.py) and [rq2_violations_parser.py](scripts/rq2_scripts/rq2_violations_parser.py) scripts into the unzipped results folder and execute them in sequence (this will generate `results_processed.csv` that is ready for analysis).

### RQ4: Comparison of DynaPyt, Dylin, and PyMOP

#### Setup

First, you need to build a Docker image (this might take a short period of time). Please run the following command in your terminal:

```bash
docker build -t pymop-rq4 -f Docker/rq4/Dockerfile .
```

#### Run experiment

Execute the following command to start one Docker instance while mounting the `workspace` folder (in the Docker container) to the same folder locally:

```bash
docker run -it --rm -v $PWD/workspace:/workspace pymop-rq4
```

Copy all the experiment scripts from the `experiment` folder into the `workspace` folder for future usage:

```bash
cd ..
cp -r /experiment/* /workspace/
cd workspace/
```

The following command will execute the RQ4 experiment with the full project list. **Note: This experiment might take days to finish.** (If you want to test out PyMOP and the experiment, please reduce the number of projects in `projects_evaluated.csv`.)

```bash
./run_experiment_rq4.sh
```

#### Results

After you finish executing the command for a list of projects, all the results will be saved as zip files in the `workspace` folder.

Copy all the zip files into a separate folder (for example, a folder named "unzipped"). Place the [unzip_file.py](scripts/unzip_file.py) script into that folder and execute it (this will unzip all the results into a new folder). Then, place the [rq4_csv_parser.py](scripts/rq4_scripts/rq4_csv_parser.py) and [rq4_violations_parser.py](scripts/rq4_scripts/rq4_violations_parser.py) scripts into the unzipped results folder and execute them in sequence (this will generate `results_processed.csv` that is ready for analysis).
