import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('algos_comparison_results.csv')

# Define the columns to check for consistency
columns_consistent = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']

# Pivot the data for easier comparison
pivoted = df.pivot(index='project', columns='algorithm', values=columns_consistent)

# ===============================
# Check for consistency for each algorithm
# ===============================

# Get the list of algorithms (excluding 'ORIGINAL')
algorithms = [col for col in pivoted.columns.levels[1] if col != 'ORIGINAL']

# Dictionary to store the count of consistent projects for each algorithm
consistent_counts = {}

# Check for consistency for each algorithm
for algo in algorithms:
    # Compare each algorithm's results to 'ORIGINAL' for all projects
    algo_vals = pivoted.xs(algo, level=1, axis=1)
    orig_vals = pivoted.xs('ORIGINAL', level=1, axis=1)
    # Both values must be notna and equal for all columns
    matches = (algo_vals == orig_vals) & algo_vals.notna() & orig_vals.notna()
    consistent = matches.all(axis=1)
    # Only count as consistent if all columns match and are not NA
    consistent_counts[algo] = consistent.sum()

# Print the number of projects with consistent results for each algorithm
print("Number of projects with consistent results for each algorithm:")
for algo, count in consistent_counts.items():
    print(f"{algo}: {count}")

# ===============================
# Check for consistency for all algorithms
# ===============================

# Calculate number of projects consistent for all algorithms
all_consistent_mask = pd.DataFrame([
    ((pivoted.xs(algo, level=1, axis=1) == pivoted.xs('ORIGINAL', level=1, axis=1)) &
     pivoted.xs(algo, level=1, axis=1).notna() &
     pivoted.xs('ORIGINAL', level=1, axis=1).notna()
    ).all(axis=1)
    for algo in algorithms
]).T
projects_consistent_all_algos = all_consistent_mask.all(axis=1).sum()

# Print the number of projects with consistent results for all algorithms
print(f"\nNumber of projects consistent for all algorithms: {projects_consistent_all_algos}")

# ===============================
# Write the consistent projects to a new CSV file
# ===============================

# Group the data for consistent projects by algorithm
consistent_projects = all_consistent_mask[all_consistent_mask.all(axis=1)]

# Write a new CSV with only projects consistent across all algorithms
consistent_project_names = consistent_projects.index
consistent_project_names_preserved = consistent_projects.index
print(len(consistent_project_names))
consistent_df = df[df['project'].isin(consistent_project_names)]
consistent_df.to_csv('algos_comparison_consistent_results.csv', index=False)

# ===============================
# Calculate the relative and absolute overhead for each algorithm
# ===============================

# Calculate the relative for each algorithm by dividing the test_duration of the algorithm by the test_duration of the original
mean_relative_overhead = {}
median_relative_overhead = {}
max_relative_overhead = {}
min_relative_overhead = {}
sum_relative_overhead = {}

# Calculate the absolute overhead for each algorithm by subtracting the test_duration of the original from the test_duration of the algorithm
mean_absolute_overhead = {}
median_absolute_overhead = {}
max_absolute_overhead = {}
min_absolute_overhead = {}
sum_absolute_overhead = {}

# Calculate the relative and absolute overhead for each algorithm
for algo in algorithms:
    # Get projects consistent for this algorithm
    algo_vals = pivoted.xs(algo, level=1, axis=1)
    orig_vals = pivoted.xs('ORIGINAL', level=1, axis=1)
    matches = (algo_vals == orig_vals) & algo_vals.notna() & orig_vals.notna()
    consistent = matches.all(axis=1)
    consistent_project_names = consistent[consistent].index

    # Get test durations for these projects only
    algo_durations = df[df['project'].isin(consistent_project_names) & (df['algorithm'] == algo)]['test_duration']
    orig_durations = df[df['project'].isin(consistent_project_names) & (df['algorithm'] == 'ORIGINAL')]['test_duration']

    # Calculate relative overhead
    relative_overhead = algo_durations.values / orig_durations.values
    mean_relative_overhead[algo] = relative_overhead.mean()
    median_relative_overhead[algo] = np.median(relative_overhead)
    max_relative_overhead[algo] = relative_overhead.max()
    min_relative_overhead[algo] = relative_overhead.min()
    sum_relative_overhead[algo] = relative_overhead.sum()

    # Calculate absolute overhead
    absolute_overhead = algo_durations.values
    mean_absolute_overhead[algo] = absolute_overhead.mean()
    median_absolute_overhead[algo] = np.median(absolute_overhead)
    max_absolute_overhead[algo] = absolute_overhead.max()
    min_absolute_overhead[algo] = absolute_overhead.min()
    sum_absolute_overhead[algo] = absolute_overhead.sum()

# Print the relative and absolute overhead for each algorithm
print("\nRelative overhead for each algorithm:")
for algo in algorithms:
    print(f"{algo}: mean={mean_relative_overhead[algo]:.2f}x, median={median_relative_overhead[algo]:.2f}x, max={max_relative_overhead[algo]:.2f}x, min={min_relative_overhead[algo]:.2f}x, sum={sum_relative_overhead[algo]:.2f}x")

print("\nAbsolute overhead for each algorithm:")
for algo in algorithms:
    print(f"{algo}: mean={mean_absolute_overhead[algo]:.2f}x, median={median_absolute_overhead[algo]:.2f}x, max={max_absolute_overhead[algo]:.2f}x, min={min_absolute_overhead[algo]:.2f}x, sum={sum_absolute_overhead[algo]:.2f}x")

# ===============================
# Write the calculated data into a macros.tex file
# ===============================

# Write the calculated data into a macros.tex file
with open('algos_comparison_stats_macros.tex', 'w') as f:
    for algo, count in consistent_counts.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_consistent_count}}{{{count}}}\n")
    for algo, count in mean_relative_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_mean_relative_overhead}}{{{count:.2f}}}\n")
    for algo, count in median_relative_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_median_relative_overhead}}{{{count:.2f}}}\n")
    for algo, count in max_relative_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_max_relative_overhead}}{{{count:.2f}}}\n")
    for algo, count in min_relative_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_min_relative_overhead}}{{{count:.2f}}}\n")
    for algo, count in sum_relative_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_sum_relative_overhead}}{{{count:.2f}}}\n")
    for algo, count in mean_absolute_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_mean_absolute_overhead}}{{{count:.2f}}}\n")
    for algo, count in median_absolute_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_median_absolute_overhead}}{{{count:.2f}}}\n")
    for algo, count in max_absolute_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_max_absolute_overhead}}{{{count:.2f}}}\n")
    for algo, count in min_absolute_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_min_absolute_overhead}}{{{count:.2f}}}\n")
    for algo, count in sum_absolute_overhead.items():
        f.write(f"\\DefMacro{{algos_comparison_{algo}_sum_absolute_overhead}}{{{count:.2f}}}\n")
    f.write(f"\\DefMacro{{algos_comparison_projects_consistent_all_algos}}{{{projects_consistent_all_algos}}}\n")
