# Discussion: The overheads of PyMOP with and without garbage collection

## Files included for this analysis:

- `gc_results.csv`: Raw performance measurements comparing PyMOP's execution with and without garbage collection across all test projects
- `projects_evaluated_gc.csv`: List of projects that were evaluated in the garbage collection analysis
- `generate-gc-macros.py`: Python script that generates LaTeX macros for performance analysis of garbage collection impact
- `gc_comparison_macros.tex`: LaTeX macros containing performance analysis results for garbage collection overhead measurements

These files contain the data and analysis scripts used to evaluate the impact of garbage collection on PyMOP's performance, including raw measurements and scripts to process these measurements.

## Steps to run these files:

1. Install Python dependencies:
   ```bash
   pip install pandas
   ```

2. Generate performance analysis macros:
   ```bash
   python generate-gc-macros.py
   ```

## Analysis results:

The generated LaTeX macros can be found in:
- `gc_comparison_macros.tex`: Analysis of PyMOP's performance metrics and overhead measurements with and without garbage collection enabled
