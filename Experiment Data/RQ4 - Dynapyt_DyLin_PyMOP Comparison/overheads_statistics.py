import sys

import pandas as pd


# Algorithm groups
ALL_4 = ['original', 'D', 'dylin', 'dynapyt', 'dynapyt_libs']
NO_LIB = ['original', 'D', 'dylin', 'dynapyt']
WITH_LIB = ['original', 'D', 'dynapyt_libs']

# Consistency check function (same as in paper_diagram.py)
def check_consistency(group):
    columns_to_check = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']
    for col in columns_to_check:
        # If any value is missing (NaN), treat as inconsistent
        if group[col].isna().any():
            return False
        if group[col].nunique() > 1:
            return False
    return True

def get_consistent_projects(data, algorithms):
    filtered = data[data['algorithm'].isin(algorithms)]
    consistency = filtered.groupby('project').apply(check_consistency)
    project_counts = filtered.groupby('project')['algorithm'].nunique()
    eligible = project_counts[project_counts == len(algorithms)].index
    consistent = consistency[consistency].index
    return list(set(eligible) & set(consistent))

def aggregate_times(data, projects, algorithms):
    result = []
    for algo in algorithms:
        df = data[(data['algorithm'] == algo) & (data['project'].isin(projects))]
        end_to_end = pd.to_numeric(df['end_to_end_time'], errors='coerce')
        instr = pd.to_numeric(df['time_instrumentation'], errors='coerce') \
              + pd.to_numeric(df['time_create_monitor'], errors='coerce') \
              + pd.to_numeric(df['post_run_time'], errors='coerce')
        monitoring = pd.to_numeric(df['test_duration'], errors='coerce')
        result.append({
            'algorithm': algo,
            'n_projects': len(df),
            'sum_end_to_end': end_to_end.sum(),
            'sum_instrumentation': instr.sum(),
            'sum_monitoring': monitoring.sum(),
        })
    return result

def calculate_speedup(data, projects, algorithms):
    result = []
    # Get pymop data and set project as index
    df_pymop = data[(data['algorithm'] == 'D') & (data['project'].isin(projects))]
    end_to_end_pymop = pd.Series(
        pd.to_numeric(df_pymop['end_to_end_time'], errors='coerce').values,
        index=df_pymop['project']
    )
    
    for algo in algorithms:
        if algo != 'original' and algo != 'D':
            df = data[(data['algorithm'] == algo) & (data['project'].isin(projects))]
            # Create series with same project index
            end_to_end = pd.Series(
                pd.to_numeric(df['end_to_end_time'], errors='coerce').values,
                index=df['project']
            )
            # Now division will work correctly as indices match
            relative_speedup = end_to_end / end_to_end_pymop
            absolute_speedup = end_to_end - end_to_end_pymop
            result.append({
                'algorithm': algo,
                'n_projects': len(df),
                'relative_speedup': relative_speedup.mean(),
                'median_relative_speedup': relative_speedup.median(),
                'min_relative_speedup': relative_speedup.min(),
                'max_relative_speedup': relative_speedup.max(),
                'absolute_speedup': absolute_speedup.mean(),
                'median_absolute_speedup': absolute_speedup.median(),
                'min_absolute_speedup': absolute_speedup.min(),
                'max_absolute_speedup': absolute_speedup.max(),
            })
    return result

def print_table(title, data):
    print(f"\n{title}")
    print(f"{'Algorithm':<15}{'Projects':>10}{'End-to-End':>15}{'Instrumentation':>20}{'Monitoring':>15}")
    for row in data:
        print(f"{row['algorithm']:<15}{row['n_projects']:>10}{row['sum_end_to_end']:>15.2f}{row['sum_instrumentation']:>20.2f}{row['sum_monitoring']:>15.2f}")

def print_speedup_table(title, data):
    print(f"\n{title}")
    print(f"{'Algorithm':<15}{'Relative Speedup':>15}{'Median Relative Speedup':>20}{'Min Relative Speedup':>15}{'Max Relative Speedup':>15}{'Absolute Speedup':>15}{'Median Absolute Speedup':>20}{'Min Absolute Speedup':>15}{'Max Absolute Speedup':>15}")
    for row in data:
        print(f"{row['algorithm']:<15}{row['relative_speedup']:>15.2f}{row['median_relative_speedup']:>20.2f}{row['min_relative_speedup']:>15.2f}{row['max_relative_speedup']:>15.2f}{row['absolute_speedup']:>15.2f}{row['median_absolute_speedup']:>20.2f}{row['min_absolute_speedup']:>15.2f}{row['max_absolute_speedup']:>15.2f}")

def save_macros(data, algo, filename):
    with open(filename, 'a') as f:
        for row in data:
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-sum-end-to-end}}{{{row['sum_end_to_end']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-sum-instrumentation}}{{{row['sum_instrumentation']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-sum-monitoring}}{{{row['sum_monitoring']:.2f}}}\n")

def save_speedup_macros(data, algo, filename):
    with open(filename, 'a') as f:
        for row in data:
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-relative-speedup}}{{{row['relative_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-median-relative-speedup}}{{{row['median_relative_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-min-relative-speedup}}{{{row['min_relative_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-max-relative-speedup}}{{{row['max_relative_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-absolute-speedup}}{{{row['absolute_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-median-absolute-speedup}}{{{row['median_absolute_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-min-absolute-speedup}}{{{row['min_absolute_speedup']:.2f}}}\n")
            f.write(f"\\DefMacro{{comparison-{algo}-{row['algorithm']}-max-absolute-speedup}}{{{row['max_absolute_speedup']:.2f}}}\n")

if __name__ == "__main__":
    # Get the file path from the command line
    if len(sys.argv) < 2:
        print("Usage: python aggregate_overhead_data.py <csv_file>")
        sys.exit(1)
    file_path = sys.argv[1]

    # Read the data from the csv file
    data = pd.read_csv(file_path)

    # Convert 'x' to NaN and make test columns numeric (to match diagram_plotting_full.py)
    test_columns = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']
    for col in test_columns:
        data[col] = pd.to_numeric(data[col].replace('x', pd.NA), errors='coerce')

    # Aggregate the data for each group
    for group, name in zip([ALL_4, NO_LIB, WITH_LIB],
                           ["All_4", "No_Lib", "With_Lib"]):
        projects = get_consistent_projects(data, group)

        # Calculate summary statistics
        agg = aggregate_times(data, projects, group)
        print_table(name, agg)
        save_macros(agg, name, f"comparison-sum-macros.tex")

        # Calculate speed up statistics
        speedup = calculate_speedup(data, projects, group)
        print_speedup_table(name, speedup)
        save_speedup_macros(speedup, name, f"comparison-speedup-macros.tex")

