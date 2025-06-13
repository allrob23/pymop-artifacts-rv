# RQ4: Comparison of PyMOP with Dynapyt and DyLin

## Files included for this RQ:
- `tools_comparison_results.csv`: Raw experimental data containing the performance measurements and comparison results between PyMOP, Dynapyt, and DyLin.
- `overheads_analysis.py`: Script for analyzing the overheads of all three tools.
- `overheads_statistics.py`: Script for computing statistical measures (mean, median, percentiles) of the relative and absolute overheads.
- `violations_analysis.py`: Script for analyzing and comparing the violations detected by each tool.
- `comparison-speedup-macros.tex`: LaTeX macros containing speedup comparison data.
- `comparison-sum-macros.tex`: LaTeX macros with aggregated summary statistics.
- `comparison-7-percentile_macros.tex`: LaTeX macros containing detailed percentile data.
- `comparison-7-statistics-macros.tex`: LaTeX macros with comprehensive statistical analysis.

These files contain the data and analysis scripts used to evaluate the violations and overheads of PyMOP, Dynapyt, and DyLin, including raw measurements, processed results, and scripts to process these measurements.

## Steps to run these files:
1. The raw data can be found in `tools_comparison_results.csv`
2. Run the analysis scripts to generate statistics and LaTeX macros:
   ```bash
   python overheads_analysis.py tools_comparison_results.csv
   python overheads_statistics.py tools_comparison_results.csv
   python violations_analysis.py tools_comparison_results.csv
   ```
3. The LaTeX files contain the formatted results for inclusion in the paper.
