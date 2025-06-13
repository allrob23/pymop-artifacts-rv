import pandas as pd

# Read the CSV file
df = pd.read_csv('instru_comparison_results.csv')

# Define the columns to check for consistency
cols = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']

# Convert 'x' in 'passed' to 0, and ensure numeric for consistency check
df['passed_numeric'] = df['passed'].replace('x', 0)
df['passed_numeric'] = pd.to_numeric(df['passed_numeric'], errors='coerce').fillna(0).astype(int)

# Define a function to check if a group of results is consistent
def is_consistent(group):
    return all(group[cols].nunique() == 1)

# Find projects with consistent results across all algorithms
consistent_projects = df.groupby('project').filter(is_consistent)['project'].unique()
df_consistent = df[df['project'].isin(consistent_projects)]

# Find projects where the "original" algorithm has 0 , '0' or 'x' in passed 
original_failed_projects = df_consistent[
    (df_consistent['algorithm'] == 'original') &
    ((df_consistent['passed'] == 0) |(df_consistent['passed'] == '0') | (df_consistent['passed'] == 'x'))
]['project'].unique()

# Exclude these projects from the final dataframe
final_df = df_consistent[~df_consistent['project'].isin(original_failed_projects)]

# Save or display the result
final_df.to_csv('instru_comparison_consistent_results.csv', index=False)
