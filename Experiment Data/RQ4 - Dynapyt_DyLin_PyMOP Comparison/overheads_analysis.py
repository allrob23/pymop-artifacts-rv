import sys

import pandas as pd
import numpy as np


# Parse the mode argument to determine which algorithms to use
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    remaining_args = sys.argv[2:]
    if len(remaining_args) > 0:
        mode = int(remaining_args[0])
        remaining_args = remaining_args[1:]
    else:
        mode = 7
else:
    raise ValueError("File path must be provided as arguments!")

# Determine which algorithms to use based on the mode
if mode == 1:
    algorithms_to_use = ['original', 'D', 'dynapyt', 'dynapyt_libs', 'dylin', 'dylin_libs']
elif mode == 2:
    algorithms_to_use = ['original', 'D', 'dynapyt', 'dylin']
elif mode == 3:
    algorithms_to_use = ['original', 'D', 'dynapyt_libs', 'dylin_libs']
elif mode == 4:
    algorithms_to_use = ['original', 'D', 'dylin', 'dylin_libs']
elif mode == 5:
    algorithms_to_use = ['original', 'D', 'dylin']
elif mode == 6:
    algorithms_to_use = ['original', 'D', 'dylin_libs']
elif mode == 7:
    algorithms_to_use = ['original', 'D', 'dynapyt', 'dynapyt_libs', 'dylin']
else:
    raise ValueError("Invalid mode!")

# Read the data from the file
data = pd.read_csv(file_path)

# Convert the test columns to numeric values
test_columns = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']
for col in test_columns:
    data[col] = pd.to_numeric(data[col].replace('x', pd.NA), errors='coerce')

def check_consistency(group):
    columns_to_check = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']
    for col in columns_to_check:
        if group[col].isna().any():
            return False
        if group[col].nunique() > 1:
            return False
    return True

def analyze_consistency(data, algorithms):
    # Filter data for the specified algorithms
    filtered_data = data[data['algorithm'].isin(algorithms)]

    # Group the filtered data by project and check consistency
    project_counts = filtered_data.groupby('project')['algorithm'].nunique()

    # Filter projects that have all algorithms present
    eligible_projects = project_counts[project_counts == len(algorithms)].index
    eligible_data = filtered_data[filtered_data['project'].isin(eligible_projects)]

    # Check test consistency for each project
    consistency_by_project = eligible_data.groupby('project', group_keys=False).apply(check_consistency)
    
    # Count how many projects are consistent
    consistent_count = consistency_by_project.sum()
    total_count = len(consistency_by_project)
    
    # Return the number of consistent projects and the total number of projects
    return consistent_count, total_count

# Analyze only the selected mode
print(f"\nAnalyzing consistency for Mode {mode} ({', '.join(algorithms_to_use)}):")
print("-" * 50)

# Analyze consistency for the selected mode and algorithms
consistent_count, total_count = analyze_consistency(data, algorithms_to_use)
print(f"Consistent projects: {consistent_count} out of {total_count}")
print(f"Consistency rate: {(consistent_count/total_count)*100:.2f}%")
print("-" * 50)

# ===============================
# Calculate the time statistics
# ===============================

# Calculate the time statistics
print(f"\nAnalyzing time statistics for Mode {mode} ({', '.join(algorithms_to_use)}):")
print("-" * 50)

# Filter consistent projects (require all algorithms present per project)
filtered_data = data[data['algorithm'].isin(algorithms_to_use)]
project_counts = filtered_data.groupby('project')['algorithm'].nunique()
eligible_projects = project_counts[project_counts == len(algorithms_to_use)].index
eligible_data = filtered_data[filtered_data['project'].isin(eligible_projects)]
consistency_by_project = filtered_data.groupby('project', group_keys=False).apply(check_consistency)
consistent_projects = consistency_by_project[consistency_by_project].index
consistent_data = eligible_data[eligible_data['project'].isin(consistent_projects)].copy()
print(f"Number of projects in consistent_data: {consistent_data['project'].nunique()}")

# Convert the time columns to numeric values
consistent_data['time_instrumentation'] = pd.to_numeric(consistent_data['time_instrumentation'], errors='coerce')
consistent_data['time_create_monitor'] = pd.to_numeric(consistent_data['time_create_monitor'], errors='coerce')
consistent_data['post_run_time'] = pd.to_numeric(consistent_data['post_run_time'], errors='coerce')

# Calculate the total instrumentation time
consistent_data['instrumentation_time'] = (
    consistent_data['time_instrumentation'] +
    consistent_data['time_create_monitor'] +
    consistent_data['post_run_time']
)

# Calculate summary statistics for each timing metric
metrics = ['instrumentation_time', 'test_duration', 'end_to_end_time']
print("\nSummary Statistics for Each Algorithm")
print("-" * 140)

D_test_duration_mean = 0
Dylin_test_duration_mean = 0

for metric in metrics:
    print(f"\n{metric.replace('_', ' ').title()}:")
    print("-" * 140)
    header = f"{'Algorithm':<20}{'Min':>12}{'Mean':>12}{'Median':>12}{'Max':>12}{'Sum':>15}"
    print(header)
    print("-" * 140)
    
    for algo in algorithms_to_use:
        algo_data = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo][metric],
            errors='coerce'
        )
        
        if not algo_data.empty:
            min_val = algo_data.min()
            mean_val = algo_data.mean()
            median_val = algo_data.median()
            max_val = algo_data.max()
            sum_val = algo_data.sum()

            if algo == 'D' and metric == 'test_duration':
                D_test_duration_mean = mean_val
            elif algo == 'dylin' and metric == 'test_duration':
                Dylin_test_duration_mean = mean_val

            # Print formatted statistics
            print(f"{algo:<20}{min_val:>12.4f}{mean_val:>12.4f}{median_val:>12.4f}{max_val:>12.4f}{sum_val:>15.4f}")
            
            # Write to LaTeX macros file
            with open(f'comparison-{mode}-statistics-macros.tex', 'a') as f:
                f.write(f"\\DefMacro{{Comparison-{mode}-algo-{algo}-{metric}-min}}{{{min_val}}}\n")
                f.write(f"\\DefMacro{{Comparison-{mode}-algo-{algo}-{metric}-mean}}{{{mean_val}}}\n") 
                f.write(f"\\DefMacro{{Comparison-{mode}-algo-{algo}-{metric}-median}}{{{median_val}}}\n")
                f.write(f"\\DefMacro{{Comparison-{mode}-algo-{algo}-{metric}-max}}{{{max_val}}}\n")
                f.write(f"\\DefMacro{{Comparison-{mode}-algo-{algo}-{metric}-sum}}{{{sum_val}}}\n")
                
    print("-" * 140)

# Calculate the mean test duraction difference between D and DyLin
D_DyLin_mean_diff = abs(D_test_duration_mean - Dylin_test_duration_mean)
print(f"Mean test duration difference between D and DyLin: {D_DyLin_mean_diff:.1f} seconds")

# Write to LaTeX macros file
with open(f'comparison-{mode}-statistics-macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{Comparison-{mode}-D-DyLin-test-duration-mean-diff}}{{{D_DyLin_mean_diff:.1f}}}\n")

# ===============================
# Calculate the relative runtime overheads
# ===============================

# Calculate the relative runtime overheads
print(f"\nAnalyzing runtime overheads for Mode {mode} ({', '.join(algorithms_to_use)}):")
print("-" * 50)

# Filter consistent projects (require all algorithms present per project)
filtered_data = data[data['algorithm'].isin(algorithms_to_use)]
project_counts = filtered_data.groupby('project')['algorithm'].nunique()
eligible_projects = project_counts[project_counts == len(algorithms_to_use)].index
eligible_data = filtered_data[filtered_data['project'].isin(eligible_projects)]
consistency_by_project = filtered_data.groupby('project', group_keys=False).apply(check_consistency)
consistent_projects = consistency_by_project[consistency_by_project].index
consistent_data = eligible_data[eligible_data['project'].isin(consistent_projects)].copy()
print(f"Number of projects in consistent_data: {consistent_data['project'].nunique()}")

# Sort projects by absolute overhead of dynapyt_libs
original_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_end_to_end_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'dynapyt_libs'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_absolute_overheads = dynapyt_libs_end_to_end_times - original_times
sorted_projects = dynapyt_libs_absolute_overheads.sort_values().index

print("\nRelative Overhead Percentiles (10th to 100th) for Each Algorithm")
print("Projects are sorted by original test execution time")
print("-" * 140)
header = f"{'Algorithm':<20}" + "".join([f"{p}th".rjust(12) for p in range(10, 101, 10)])
print(header)
print("-" * 140)

for algo in algorithms_to_use:
    if algo != 'original':
        algo_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo].set_index('project')['end_to_end_time'],
            errors='coerce'
        )
        orig_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'],
            errors='coerce'
        )

        # Calculate relative overheads for sorted projects
        relative_overheads = []
        for project in sorted_projects:
            if project in algo_times.index and project in orig_times.index:
                t_algo = algo_times[project]
                t_orig = orig_times[project]
                if not pd.isna(t_algo) and not pd.isna(t_orig) and t_orig > 0:
                    relative_overheads.append(t_algo - t_orig)

        if relative_overheads:
            relative_overheads_by_bucket = {}

            # Split the relative overhead into 10 buckets
            counter = 0
            for p in range(1, 11):
                end = round(len(relative_overheads) / 10 * p)
                bucket = relative_overheads[counter:end]
                relative_overheads_by_bucket[p] = bucket
                counter = end

            # Calculate the min, max, mean, median, and sum of the relative overheads for each bucket
            relative_overheads_by_bucket_stats = {}
            for p in range(1, 11):
                bucket = relative_overheads_by_bucket[p]
                relative_overheads_by_bucket_stats[p] = {
                    'min': min(bucket),
                    'max': max(bucket),
                    'mean': sum(bucket) / len(bucket),
                    'median': np.median(bucket),
                    'sum': sum(bucket)
                }

            # Print the average values in a table format
            values = "".join([f"{relative_overheads_by_bucket_stats[p]['mean']:>11.2f}x" for p in range(1, 11)])
            print(f"{algo:<20}{values}")

            # Write LaTeX macros to file
            with open(f'comparison-{mode}-percentile_macros.tex', 'a') as f:
                for p in range(1, 11):
                    for key, value in relative_overheads_by_bucket_stats[p].items():
                        # Format the value to 2 decimal places and remove the 'x' suffix
                        value = f"{value}"
                        # Create macro name based on algorithm and percentile
                        macro_name = f"\\DefMacro{{Comparison-{mode}-algo-{algo}-p{p}-overhead-{key}}}{{{value}}}\n"
                        f.write(macro_name)

print("-" * 140)

# ===============================
# Calculate the relative instrumentation overheads
# ===============================

# Calculate the relative instrumentation overheads
print(f"\nAnalyzing instrumentation overheads for Mode {mode} ({', '.join(algorithms_to_use)}):")
print("-" * 50)

# Filter consistent projects (require all algorithms present per project)
filtered_data = data[data['algorithm'].isin(algorithms_to_use)]
project_counts = filtered_data.groupby('project')['algorithm'].nunique()
eligible_projects = project_counts[project_counts == len(algorithms_to_use)].index
eligible_data = filtered_data[filtered_data['project'].isin(eligible_projects)]
consistency_by_project = filtered_data.groupby('project', group_keys=False).apply(check_consistency)
consistent_projects = consistency_by_project[consistency_by_project].index
consistent_data = eligible_data[eligible_data['project'].isin(consistent_projects)].copy()
print(f"Number of projects in consistent_data: {consistent_data['project'].nunique()}")

# Sort projects by absolute overhead of dynapyt_libs
original_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_end_to_end_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'dynapyt_libs'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_absolute_overheads = dynapyt_libs_end_to_end_times - original_times
sorted_projects = dynapyt_libs_absolute_overheads.sort_values().index

print("\nRelative Instrumentation Overhead Percentiles (10th to 100th) for Each Algorithm")
print("Projects are sorted by original test execution time")
print("-" * 140)
header = f"{'Algorithm':<20}" + "".join([f"{p}th".rjust(12) for p in range(10, 101, 10)])
print(header)
print("-" * 140)

for algo in algorithms_to_use:
    if algo != 'original':
        algo_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo].set_index('project')['time_instrumentation'],
            errors='coerce'
        ) + pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo].set_index('project')['time_create_monitor'],
            errors='coerce'
        ) + pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo].set_index('project')['post_run_time'],
            errors='coerce'
        )

        orig_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'],
            errors='coerce'
        )

        # Calculate relative overheads for sorted projects
        relative_overheads = []
        for project in sorted_projects:
            if project in algo_times.index and project in orig_times.index:
                t_algo = algo_times[project]
                t_orig = orig_times[project]
                if not pd.isna(t_algo) and not pd.isna(t_orig) and t_orig > 0:
                    relative_overheads.append(t_algo - t_orig)

        if relative_overheads:
            relative_overheads_by_bucket = []

            # Split the relative overhead into 10 buckets
            counter = 0
            for p in range(1, 11):
                end = round(len(relative_overheads) / 10 * p)
                bucket = relative_overheads[counter:end]
                relative_overheads_by_bucket.append(bucket)
                counter = end

            # Calculate the min, max, mean, median, and sum of the relative overheads for each bucket
            relative_overheads_by_bucket_stats = []
            for bucket in relative_overheads_by_bucket:
                relative_overheads_by_bucket_stats.append({
                    'min': min(bucket),
                    'max': max(bucket),
                    'mean': sum(bucket) / len(bucket),
                    'median': np.median(bucket),
                    'sum': sum(bucket)
                })

            # Print the average values in a table format
            values = "".join([f"{p['mean']:>11.2f}x" for p in relative_overheads_by_bucket_stats])
            print(f"{algo:<20}{values}")

            # Write LaTeX macros to file
            with open(f'comparison-{mode}-percentile_macros.tex', 'a') as f:
                for i, p in enumerate(relative_overheads_by_bucket_stats):
                    for key, value in p.items():
                        # Format the value to 2 decimal places and remove the 'x' suffix
                        value = f"{value}"
                        # Create macro name based on algorithm and percentile
                        macro_name = f"\\DefMacro{{Comparison-{mode}-algo-{algo}-p{i+1}-instrumentation-overhead-{key}}}{{{value}}}\n"
                        f.write(macro_name)

print("-" * 140)

# ===============================
# Calculate the relative monitoring overheads
# ===============================

# Calculate the relative monitoring overheads
print(f"\nAnalyzing monitoring overheads for Mode {mode} ({', '.join(algorithms_to_use)}):")
print("-" * 50)

# Filter consistent projects (require all algorithms present per project)
filtered_data = data[data['algorithm'].isin(algorithms_to_use)]
project_counts = filtered_data.groupby('project')['algorithm'].nunique()
eligible_projects = project_counts[project_counts == len(algorithms_to_use)].index
eligible_data = filtered_data[filtered_data['project'].isin(eligible_projects)]
consistency_by_project = filtered_data.groupby('project', group_keys=False).apply(check_consistency)
consistent_projects = consistency_by_project[consistency_by_project].index
consistent_data = eligible_data[eligible_data['project'].isin(consistent_projects)].copy()
print(f"Number of projects in consistent_data: {consistent_data['project'].nunique()}")

# Sort projects by the absolute overhead of dynapyt_libs
original_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_end_to_end_times = pd.to_numeric(consistent_data[consistent_data['algorithm'] == 'dynapyt_libs'].set_index('project')['end_to_end_time'], errors='coerce')
dynapyt_libs_absolute_overheads = dynapyt_libs_end_to_end_times - original_times
sorted_projects = dynapyt_libs_absolute_overheads.sort_values().index

print("\nRelative Monitoring Overhead Percentiles (10th to 100th) for Each Algorithm")
print("Projects are sorted by original test execution time")
print("-" * 140)
header = f"{'Algorithm':<20}" + "".join([f"{p}th".rjust(12) for p in range(10, 101, 10)])
print(header)
print("-" * 140)

for algo in algorithms_to_use:
    if algo != 'original':
        algo_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == algo].set_index('project')['test_duration'],
            errors='coerce'
        )

        orig_times = pd.to_numeric(
            consistent_data[consistent_data['algorithm'] == 'original'].set_index('project')['end_to_end_time'],
            errors='coerce'
        )

        # Calculate relative overheads for sorted projects
        relative_overheads = []
        for project in sorted_projects:
            if project in algo_times.index and project in orig_times.index:
                t_algo = algo_times[project]
                t_orig = orig_times[project]
                if not pd.isna(t_algo) and not pd.isna(t_orig) and t_orig > 0:
                    relative_overheads.append(t_algo - t_orig)

        if relative_overheads:
            relative_overheads_by_bucket = []

            # Split the relative overhead into 10 buckets
            counter = 0
            for p in range(1, 11):
                end = round(len(relative_overheads) / 10 * p)
                bucket = relative_overheads[counter:end]
                relative_overheads_by_bucket.append(bucket)
                counter = end

            # Calculate the min, max, mean, median, and sum of the relative overheads for each bucket
            relative_overheads_by_bucket_stats = []
            for bucket in relative_overheads_by_bucket:
                relative_overheads_by_bucket_stats.append({
                    'min': min(bucket),
                    'max': max(bucket),
                    'mean': sum(bucket) / len(bucket),
                    'median': np.median(bucket),
                    'sum': sum(bucket)
                })

            # Print the average values in a table format
            values = "".join([f"{p['mean']:>11.2f}x" for p in relative_overheads_by_bucket_stats])
            print(f"{algo:<20}{values}")

            # Write LaTeX macros to file
            with open(f'comparison-{mode}-percentile_macros.tex', 'a') as f:
                for i, p in enumerate(relative_overheads_by_bucket_stats):
                    for key, value in p.items():
                        # Format the value to 2 decimal places and remove the 'x' suffix
                        value = f"{value}"
                        # Create macro name based on algorithm and percentile
                        macro_name = f"\\DefMacro{{Comparison-{mode}-algo-{algo}-p{i+1}-monitoring-overhead-{key}}}{{{value}}}\n"
                        f.write(macro_name)

print("-" * 140)

# Print the total number of consistent projects
print(f"Total consistent projects analyzed: {consistent_data['project'].nunique()}")
with open(f'comparison-{mode}-percentile_macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{Comparison-{mode}-total-projects}}{{{consistent_data['project'].nunique()}}}\n")