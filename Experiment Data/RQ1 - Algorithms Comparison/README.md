# RQ1: The overheads of PyMOP's monitoring algorithms

## Files included for this RQ:

- `algos_comparison_results.csv`: Raw performance measurements comparing all monitoring algorithms (B, C, C+, and D) of PyMOP across all test projects
- `algos_comparison_consistent_results.csv`: Filtered dataset containing only projects that demonstrate consistent test results across all algorithms (B, C, C+, and D)
- `algos_comparison_consistent_time_results.csv`: Processed execution time measurements for each algorithm, derived from the consistent results dataset
- `last_decile_projects.csv`: List of projects that exhibited the highest overhead (top 10%) across all monitoring algorithms
- `generate-algos-comparison-macros.py`: Python script that generates LaTeX macros for performance analysis of all algorithms (B, C, C+, and D)
- `algos-comparison-overhead-fastest-macros.tex`: LaTeX macros containing performance analysis of all algorithms (B, C, C+, and D)
- `algos_comparison_stats_macros.tex`: LaTeX macros containing statistical results of all algorithms (B, C, C+, and D)
- `algos_comparison_time_parser.py`: Script that processes `algos_comparison_consistent_results.csv` to extract and format execution time data into `algos_comparison_consistent_time_results.csv`
- `consistency_checker.py`: Validation script that ensures test result consistency is maintained across all algorithms for each project

These files contain the data and analysis scripts used to evaluate the overheads of different monitoring algorithms in PyMOP, including raw measurements, processed results, and scripts to process these measurements.

## Steps to run these files:

1. Validate the raw results for test results consistency:
   ```bash
   python consistency_checker.py
   ```

2. Parse the filtered results to generate the time results file:
   ```bash
   python algos_comparison_time_parser.py
   ```

3. Generate performance analysis macros:
   ```bash
   python generate-algos-comparison-macros.py algos_comparison_consistent_time_results.csv
   ```

## Analysis results:

The generated LaTeX macros can be found in:
- `algos-comparison-overhead-fastest-macros.tex`: Analysis of algorithm performance
- `algos_comparison_stats_macros.tex`: Statistical results of algorithm performance