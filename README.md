# A Generic and Efficient Python Runtime Verification System and its Large-scale Evaluation

## Appendix

The appendix is available [here](appendix.pdf). It contains:
* A detailed comparison of instrumentation strategies (discussed in Section 3)
* Our submitted PRs and issues (both accepted and rejected) from RQ3

## Projects and Data

This repository contains the following data at locations in the following hyperlinks:

* [List of projects used in all RQs (including their GitHub URLs and commit SHAs)](Experiment_Data/projects_evaluated.csv)
* [Experiment data for RQ1: Comparison of PyMOP Online Algorithms](Experiment_Data/RQ1%20-%20Algorithms%20Comparison/)
* [Experiment data for RQ2: Comparison of PyMOP Instrumentation Strategies](Experiment_Data/RQ2%20-%20Instrumentation%20Strategies%20Comparison/)
* [Experiment data for RQ4: Comparison of DynaPyt, Dylin, and PyMOP](Experiment_Data/RQ4%20-%20Dynapyt_DyLin_PyMOP%20Comparison/)
* [Experiment data for Discussions](Experiment_Data/Discussion)

## Repository Structure

| Directory / File   | Purpose                                                      |
| ------------------ | ------------------------------------------------------------ |
| appendix.pdf       | Contains detailed supplementary information discussed in the paper |
| Docker             | Contains multiple Dockerfiles that can be built to run all RQ experiments |
| Experiment_Data    | Contains project information and experiment data for all RQs and discussions |
| pymop              | Contains the source code of PyMOP                            |
| scripts            | Contains scripts to run all RQ and Discussion experiments and parse the results |

## Usage

### Prerequisites

* An x86-64 architecture machine
* Ubuntu 22.04
* [Docker](https://docs.docker.com/get-docker/)

### RQ1: The overheads of PyMOP's monitoring algorithms

#### Setup

This is a Docker-based configuration to run RQ1 experiment. Follow the steps below to get started:

1. Open the right directory in the repo

```bash
cd ./Docker/rq1/
```

2. Build the Docker image (this might take a short period of time)

```bash
python3 ./src/build-container.py
```

3. Place the project links in `project-links.csv` file with the following header (it is pre-populated with the projects from [here](Experiment_Data/projects_evaluated.csv):

```csv
link,sha
```

4. Run the experiment using the following command (replace `<max_concurrent_containers>` with the desired number of concurrent containers.) **Note: This experiment might take days to finish.** (If you want to test out PyMOP and the experiment, please reduce the number of projects in `project-links.csv`.):

```bash
python3 ./src/run-experiment.py <max_concurrent_containers>
```

That's it! The script will handle the rest. The results will be saved in the `Docker/rq1/results/` directory.
While the program is running the file `Docker/rq1/results/runs.csv` will update the run status of each project/algo.

5.  To get the csv of the results you can run

```bash
bash ./src/organize_output.sh
python3 ./src/parse-reports.py
```

#### Results

The results will be in `Docker/rq1/results/results.csv`. This contais detailed information on each run of each project including time, memory, and violations.

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

Copy all the zip files into a separate folder (for example, a folder named `rq2_results`). Place the [unzip_file.py](scripts/unzip_file.py) script into that folder and execute it (this will unzip all the results into a new folder `rq2_results_unzipped`). Then, place the [rq2_csv_parser.py](scripts/rq2_scripts/rq2_csv_parser.py) and [rq2_violations_parser.py](scripts/rq2_scripts/rq2_violations_parser.py) scripts into the unzipped results folder and execute them in sequence (this will generate `results_processed.csv` that is ready for analysis).

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

Copy all the zip files into a separate folder (for example, a folder named `rq4_results`). Place the [unzip_file.py](scripts/unzip_file.py) script into that folder and execute it (this will unzip all the results into a new folder `rq4_results_unzipped`). Then, place the [rq4_csv_parser.py](scripts/rq4_scripts/rq4_csv_parser.py) and [rq4_violations_parser.py](scripts/rq4_scripts/rq4_violations_parser.py) scripts into the unzipped results folder and execute them in sequence (this will generate `results_processed.csv` that is ready for analysis).


### Discussion: Offline Algorithm

#### Setup

Similar to how RQ1 experiment is run, this experiment can be run by followig the steps bellow:

1. open the directory

```sh
cd ./Docker/Discussion/algorithm-a
```

2. Build the Docker image (this might take a while)

   ```sh
   python3 ./src/build-container.py
   ```

3. Place the project links in `project-links.csv` file with the following header (it is pre-populated with the projects we used for this experiment [here](Experiment_Data/Discussion/Offline%20Algorithm/projects_evaluated_algoA.csv)):

```csv
link,sha
```

4. Run the experiment using the following command (replace `<max_concurrent_containers>` with the desired number of concurrent containers.) This will take very long:

```sh
python3 ./src/run-experiment.py <max_concurrent_containers>
```

That's it! The script will handle the rest. The results will be saved in the `Docker/Discussion/algorithm-a/results/` directory.
While the program is running the file `Docker/Discussion/algorithm-a/results/runs.csv` will update the run status of each project/algo.

5.  To get the csv of the results you can run

```sh
bash ./src/organize_output.sh
python3 ./src/parse-reports.py
```

#### Results

The results will be in `Docker/Discussion/algorithm-a/results/results.csv`. This contais detailed information on each run of each project including time, memory, and violations.
