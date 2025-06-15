import pandas as pd


df = pd.read_csv('algoA_results.csv')

# Pivot the DataFrame to have algorithms as columns and projects as rows
pivot_df = df.pivot(index='project', columns='algorithm', values='end_to_end_time')
project_names = pivot_df.index

# Calculate statistics for total events for each algorithm, only for slower projects
print("\nTotal events statistics for each algorithm (only for slower projects):")

# Create a list to store stats for each algorithm
stats_list = []
for algo in ['A', 'B', 'C', 'C+', 'D']:
    # Filter df for both the algorithm and the slower projects
    filtered_df = df[(df['algorithm'] == algo) & (df['project'].isin(project_names))]
    stats = filtered_df['total_events'].agg(['min', 'max', 'mean', 'median', 'sum'])
    stats_dict = {
        'Algorithm': algo,
        'Min': f"{stats['min']:.2f}",
        'Max': f"{stats['max']:.2f}",
        'Mean': f"{stats['mean']:.2f}",
        'Median': f"{stats['median']:.2f}",
        'Sum': f"{stats['sum']:.2f}"
    }
    stats_list.append(stats_dict)

# Create and display the table
stats_df = pd.DataFrame(stats_list)
print("\n" + stats_df.to_string(index=False))

# Get the algorithms to compare
algorithms = [col for col in pivot_df.columns if col != 'ORIGINAL']

# DataFrames to store overheads
absolute_overhead_df = pivot_df[algorithms].subtract(pivot_df['ORIGINAL'], axis=0)
relative_overhead_df = pivot_df[algorithms].divide(pivot_df['ORIGINAL'], axis=0)

# Function to print stats
def print_stats(df, label):
    print(f"\n{label} overhead compared to ORIGINAL:")
    stats = df.agg(['mean', 'median', 'sum', 'min', 'max'])
    print(stats)

# Write the statistics into macros
with open('algo_a_overhead_macros.tex', 'w') as f:
    f.write(f"\\DefMacro{{algo_a_comparison_total_projects}}{{{len(project_names)}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_relative_overhead_mean}}{{{relative_overhead_df['A'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_relative_overhead_mean}}{{{relative_overhead_df['B'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_relative_overhead_mean}}{{{relative_overhead_df['C'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_relative_overhead_mean}}{{{relative_overhead_df['C+'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_relative_overhead_mean}}{{{relative_overhead_df['D'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_relative_overhead_median}}{{{relative_overhead_df['A'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_relative_overhead_median}}{{{relative_overhead_df['B'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_relative_overhead_median}}{{{relative_overhead_df['C'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_relative_overhead_median}}{{{relative_overhead_df['C+'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_relative_overhead_median}}{{{relative_overhead_df['D'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_relative_overhead_min}}{{{relative_overhead_df['A'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_relative_overhead_min}}{{{relative_overhead_df['B'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_relative_overhead_min}}{{{relative_overhead_df['C'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_relative_overhead_min}}{{{relative_overhead_df['C+'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_relative_overhead_min}}{{{relative_overhead_df['D'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_relative_overhead_max}}{{{relative_overhead_df['A'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_relative_overhead_max}}{{{relative_overhead_df['B'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_relative_overhead_max}}{{{relative_overhead_df['C'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_relative_overhead_max}}{{{relative_overhead_df['C+'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_relative_overhead_max}}{{{relative_overhead_df['D'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_relative_overhead_sum}}{{{relative_overhead_df['A'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_relative_overhead_sum}}{{{relative_overhead_df['B'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_relative_overhead_sum}}{{{relative_overhead_df['C'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_relative_overhead_sum}}{{{relative_overhead_df['C+'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_relative_overhead_sum}}{{{relative_overhead_df['D'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_absolute_overhead_mean}}{{{absolute_overhead_df['A'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_absolute_overhead_mean}}{{{absolute_overhead_df['B'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_absolute_overhead_mean}}{{{absolute_overhead_df['C'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_absolute_overhead_mean}}{{{absolute_overhead_df['C+'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_absolute_overhead_mean}}{{{absolute_overhead_df['D'].mean():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_absolute_overhead_median}}{{{absolute_overhead_df['A'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_absolute_overhead_median}}{{{absolute_overhead_df['B'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_absolute_overhead_median}}{{{absolute_overhead_df['C'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_absolute_overhead_median}}{{{absolute_overhead_df['C+'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_absolute_overhead_median}}{{{absolute_overhead_df['D'].median():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_absolute_overhead_min}}{{{absolute_overhead_df['A'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_absolute_overhead_min}}{{{absolute_overhead_df['B'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_absolute_overhead_min}}{{{absolute_overhead_df['C'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_absolute_overhead_min}}{{{absolute_overhead_df['C+'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_absolute_overhead_min}}{{{absolute_overhead_df['D'].min():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_absolute_overhead_max}}{{{absolute_overhead_df['A'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_absolute_overhead_max}}{{{absolute_overhead_df['B'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_absolute_overhead_max}}{{{absolute_overhead_df['C'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_absolute_overhead_max}}{{{absolute_overhead_df['C+'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_absolute_overhead_max}}{{{absolute_overhead_df['D'].max():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_A_absolute_overhead_sum}}{{{absolute_overhead_df['A'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_B_absolute_overhead_sum}}{{{absolute_overhead_df['B'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C_absolute_overhead_sum}}{{{absolute_overhead_df['C'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_C+_absolute_overhead_sum}}{{{absolute_overhead_df['C+'].sum():.2f}}}\n")
    f.write(f"\\DefMacro{{algo_a_comparison_D_absolute_overhead_sum}}{{{absolute_overhead_df['D'].sum():.2f}}}\n")

print_stats(absolute_overhead_df, "Absolute")
print_stats(relative_overhead_df, "Relative")
