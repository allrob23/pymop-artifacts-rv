import pandas as pd
import numpy as np
from tabulate import tabulate

# Read CSV file
csv_file = 'instru_comparison_consistent_results.csv'  # Replace with your CSV file path
data = pd.read_csv(csv_file)

# Define the strategies
strategies = ['original', 'monkey patching', 'curse', 'ast']
violation_strategies = ['monkey patching', 'curse', 'ast']

# Define builtin violation names
builtin_violations = {
    'KeyInList', 'UnsafeListIterator', 'UnsafeMapIterator', 'UnsafeDictIterator',
    'PyDocs_MustSortBeforeGroupBy', 'Arrays_SortBeforeBinarySearch', 'UnsafeArrayIterator'
}

def clean_missing_strategies(df, strategies):
    """Remove projects that don't have results for all specified strategies."""
    strategy_counts = df.groupby('project')['type_project'].nunique()
    expected_strategy_count = len(strategies)
    projects_with_missing_strategies = strategy_counts[strategy_counts < expected_strategy_count].index.tolist()
    cleaned_df = df[~df['project'].isin(projects_with_missing_strategies)]
    return cleaned_df

def clean_time_violation_data(df):
    """Clean the dataset by removing projects with inconsistent passed/failed tests or 'x' values."""
    failed_projects = df[df['passed'].astype(str) == 'x']['project'].unique()
    failed_projects = set(failed_projects) | set(df[df['failed'].astype(str) == 'x']['project'].unique())
    df_cleaned = df[~df['project'].isin(failed_projects)]

    projects_to_remove = []
    for project in df_cleaned['project'].unique():
        project_data = df_cleaned[df_cleaned['project'] == project]
        passed_counts = project_data.groupby('type_project')['passed'].first()
        failed_counts = project_data.groupby('type_project')['failed'].first()
        
        expected_strategies = {'monkey patching', 'curse', 'ast', 'original'}
        if set(passed_counts.index) != expected_strategies or set(failed_counts.index) != expected_strategies:
            projects_to_remove.append(project)
            continue
        
        if not (passed_counts.nunique() == 1 and failed_counts.nunique() == 1):
            projects_to_remove.append(project)

    df_cleaned = df_cleaned[~df_cleaned['project'].isin(projects_to_remove)]

    # Sum 'time_instrumentation' and 'time_create_monitor' for each row and store in 'time_instrumentation'
    if 'time_create_monitor' in df_cleaned.columns:
        df_cleaned['time_instrumentation'] = pd.to_numeric(df_cleaned['time_instrumentation'], errors='coerce').fillna(0) + pd.to_numeric(df_cleaned['time_create_monitor'], errors='coerce').fillna(0)

    for col in ['time_instrumentation', 'test_duration', 'end_to_end_time', 'total_violations']:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

    return df_cleaned

def clean_pass_fail_data(df):
    """Remove projects where any run has 'passed' or 'failed' equal to 'x'."""
    df = df.copy()
    df['passed'] = df['passed'].astype(str)
    df['failed'] = df['failed'].astype(str)

    failed_projects = df[(df['passed'] == 'x') | (df['failed'] == 'x')]['project'].unique()
    cleaned_df = df[~df['project'].isin(failed_projects)]
    
    cleaned_df['passed'] = pd.to_numeric(cleaned_df['passed'], errors='coerce')
    cleaned_df['failed'] = pd.to_numeric(cleaned_df['failed'], errors='coerce')
    
    return cleaned_df

def compute_stats(df, column):
    """Compute mean, median, max, min for a column grouped by type_project."""
    df = df.copy()
    df[column] = pd.to_numeric(df[column], errors='coerce')
    stats = df.groupby('type_project')[column].agg(['mean', 'median', 'max', 'min', 'sum']).reset_index()
    return stats

def get_all_unique_violations(df):
    """Count globally unique violation locations (including line numbers) across all strategies."""
    print('df length', len(df))
    unique_violations = set()

    for _, row in df.iterrows():
        violations_str = row.get('violations_by_location', '')

        if pd.isna(violations_str) or not violations_str:
            continue

        locations = violations_str.split(';')
        for loc in locations:
            try:
                path_line, _ = loc.split('=')
                path = path_line.strip()  # Keep line number
                unique_violations.add(path)
            except (ValueError, IndexError):
                continue

    return len(unique_violations)

def parse_violations_by_location(df):
    """Parse violations by location into categories (python_source, site_packages, project_under_test)."""
    strategy_paths = {}
    for _, row in df.iterrows():
        strategy = row.get("type_project")
        violations_str = row.get("violations_by_location", "")
        if pd.isna(violations_str) or not violations_str:
            continue
        if strategy not in strategy_paths:
            strategy_paths[strategy] = {
                "python_source": set(),
                "site_packages": set(),
                "project_under_test": set()
            }
        for entry in violations_str.split(';'):
            if '=' in entry:
                path = entry.split('=')[0].strip()
                if path.startswith("/usr/lib/python"):
                    strategy_paths[strategy]["python_source"].add(path)
                elif "site-packages" in path:
                    strategy_paths[strategy]["site_packages"].add(path)
                elif "/workspace/" in path:
                    strategy_paths[strategy]["project_under_test"].add(path)
                else:
                    strategy_paths[strategy]["python_source"].add(path)
    data = []
    for strategy, paths in strategy_paths.items():
        data.append({
            "type_project": strategy,
            "python_source": len(paths["python_source"]),
            "site_packages": len(paths["site_packages"]),
            "project_under_test": len(paths["project_under_test"])
        })
    return pd.DataFrame(data)

def parse_violations_by_type(df):
    """Parse the 'violations' column and categorize violations by type (builtin, non_builtin)."""
    data = []
    for _, row in df.iterrows():
        strategy = row['type_project']
        violations_str = row['violations']
        builtin = 0
        non_builtin = 0
        if pd.isna(violations_str) or not violations_str:
            data.append({
                'type_project': strategy,
                'builtin': builtin,
                'non_builtin': non_builtin
            })
            continue
        violations = violations_str.split(';')
        for viol in violations:
            if not viol:
                continue
            try:
                name, count = viol.split('=')
                count = int(count)
                if name in builtin_violations:
                    builtin += count
                else:
                    non_builtin += count
            except (ValueError, IndexError):
                continue
        data.append({
            'type_project': strategy,
            'builtin': builtin,
            'non_builtin': non_builtin
        })
    violations_by_type = pd.DataFrame(data)
    violations_by_type = violations_by_type.groupby('type_project').sum().reset_index()
    return violations_by_type

def compute_box_plot_stats(data, column, strategies):
    """Compute box plot statistics (whiskers, quartiles, median) for a column."""
    stats = []
    for strategy in strategies:
        values = pd.to_numeric(data[data['type_project'] == strategy][column], errors='coerce').dropna()
        if len(values) < 2:
            stats.append({
                'type_project': strategy,
                'lower_whisker': 0,
                'lower_quartile': 0,
                'median': 0,
                'upper_quartile': 0,
                'upper_whisker': 0
            })
            continue
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        median = np.median(values)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        lower_whisker = max(values[values >= lower_bound].min(), values.min()) if len(values) > 0 else 0
        upper_whisker = min(values[values <= upper_bound].max(), values.max()) if len(values) > 0 else 0
        stats.append({
            'type_project': strategy,
            'lower_whisker': lower_whisker,
            'lower_quartile': q1,
            'median': median,
            'upper_quartile': q3,
            'upper_whisker': upper_whisker
        })
    return pd.DataFrame(stats)

def compute_violations_by_origin_box_plot_stats(data, strategies):
    """Compute box plot statistics for violations by origin."""
    project_data = []
    for _, row in data.iterrows():
        project = row['project']
        strategy = row['type_project']
        violations_str = row['violations_by_location']
        python_source = set()
        site_packages = set()
        project_under_test = set()
        if pd.isna(violations_str) or not violations_str:
            project_data.append({
                'project': project,
                'type_project': strategy,
                'python_source': len(python_source),
                'site_packages': len(site_packages),
                'project_under_test': len(project_under_test)
            })
            continue
        locations = violations_str.split(';')
        for loc in locations:
            if not loc:
                continue
            try:
                path_line, count = loc.split('=')
                count = int(count)
                path = path_line.split(':')[0]
                if path.startswith('/usr/lib/python'):
                    python_source.add(path)
                elif 'site-packages' in path:
                    site_packages.add(path)
                elif '/workspace/' in path:
                    project_under_test.add(path)
            except (ValueError, IndexError):
                continue
        project_data.append({
            'project': project,
            'type_project': strategy,
            'python_source': len(python_source),
            'site_packages': len(site_packages),
            'project_under_test': len(project_under_test)
        })
    df = pd.DataFrame(project_data)
    origins = ['python_source', 'site_packages', 'project_under_test']
    stats = []
    for strategy in strategies:
        for origin in origins:
            values = df[df['type_project'] == strategy][origin].dropna()
            if len(values) < 2:
                stats.append({
                    'type_project': strategy,
                    'origin': origin,
                    'lower_whisker': 0,
                    'lower_quartile': 0,
                    'median': 0,
                    'upper_quartile': 0,
                    'upper_whisker': 0
                })
                continue
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            median = np.median(values)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            lower_whisker = max(values[values >= lower_bound].min(), values.min()) if len(values) > 0 else 0
            upper_whisker = min(values[values <= upper_bound].max(), values.max()) if len(values) > 0 else 0
            stats.append({
                'type_project': strategy,
                'origin': origin,
                'lower_whisker': lower_whisker,
                'lower_quartile': q1,
                'median': median,
                'upper_quartile': q3,
                'upper_whisker': upper_whisker
            })
    return pd.DataFrame(stats)

def compute_fastest_strategy(df, strategies, column='end_to_end_time'):
    """Identify the fastest strategy per project based on the specified column."""
    df = df[df['type_project'].isin(strategies)].copy()
    df[column] = pd.to_numeric(df[column], errors='coerce')
    df = df.dropna(subset=[column])
    pivot_df = df.pivot(index='project', columns='type_project', values=column)
    pivot_df = pivot_df.dropna()
    fastest_strategy = pivot_df.idxmin(axis=1)
    fastest_df = pd.DataFrame({
        'project': fastest_strategy.index,
        'fastest_strategy': fastest_strategy.values
    })
    return fastest_df

def compute_fastest_strategy_per_percentile(df, strategies, column='end_to_end_time'):
    """Compute the number of projects where each strategy is the fastest per percentile bin."""
    df = df[df['type_project'].isin(strategies)].copy()
    df[column] = pd.to_numeric(df[column], errors='coerce')
    df = df.dropna(subset=[column])
    pivot_df = df.pivot(index='project', columns='type_project', values=column)
    pivot_df = pivot_df.dropna()
    fastest_strategy = pivot_df.idxmin(axis=1)
    min_times = pivot_df.min(axis=1)
    fastest_df = pd.DataFrame({
        'project': fastest_strategy.index,
        'fastest_strategy': fastest_strategy.values,
        'min_time': min_times.values
    })
    percentile_bins = np.percentile(fastest_df['min_time'].dropna(), np.arange(0, 101, 10))
    percentile_bins = np.unique(percentile_bins)
    if len(percentile_bins) != 11:
        percentile_bins = np.linspace(fastest_df['min_time'].min(), fastest_df['min_time'].max(), 11)
    bin_labels = [f"{int(i)}to{int(i+10)}" for i in range(0, 100, 10)]
    fastest_df['percentile_bin'] = pd.cut(fastest_df['min_time'], bins=percentile_bins, labels=bin_labels, include_lowest=True)
    counts = fastest_df.groupby(['percentile_bin', 'fastest_strategy']).size().unstack(fill_value=0).reset_index()
    for strategy in strategies:
        if strategy not in counts.columns:
            counts[strategy] = 0
    return counts, bin_labels

def format_macro_name(name):
    """Format strategy names for LaTeX macros."""
    name = name.replace(' ', '')
    return name[0].upper() + name[1:]

def compute_unique_violations_by_strategy(violation_str):
    """Compute the number of unique violations for each strategy."""
    violations = violation_str.split(';')
    total_count = 0
    for violation in violations:
        if not violation:
            continue
        violation_name, count = violation.split('=')
        total_count += int(count)
    return total_count

def compute_unique_violations(df):
    """Compute the number of unique violations for each strategy."""
    df = df.copy()
    df['unique_violations_count'] = df['unique_violations_count'].fillna('')
    df['unique_violations_count'] = df['unique_violations_count'].apply(compute_unique_violations_by_strategy)
    return df

def generate_variables_latex():
    """Generate LaTeX macros for all variables in variables.tex and print data to terminal."""
    latex = r""""""

    # Data cleaning
    data_cleaned = clean_missing_strategies(data, strategies)

    # Total number of projects
    total_projects = data_cleaned['project'].nunique()
    print(f"\n{'='*80}\nTotal Number of Projects\n{'='*80}")
    print(f"Total Projects: {total_projects:,}\n")

    time_data = clean_time_violation_data(data_cleaned)
    pass_fail_data = clean_pass_fail_data(data_cleaned)
    viol_data = time_data[time_data['type_project'].isin(violation_strategies)]

    # Compute fastest strategy per project
    fastest_df = compute_fastest_strategy(time_data, violation_strategies, 'end_to_end_time')

    # 1. Instrumentation Time Statistics
    print(f"\n{'='*80}\n1. Instrumentation Time Statistics (Table 1)\n{'='*80}")
    instr_stats = compute_stats(time_data, 'time_instrumentation')
    instr_stats_display = instr_stats.copy()
    instr_stats_display[['mean', 'median', 'max', 'min', 'sum']] = instr_stats_display[['mean', 'median', 'max', 'min', 'sum']].round(2)
    print(tabulate(instr_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in instr_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Instrumentation Time Statistics (Table 1)\n"
        latex += f"\\DefMacro{{InstrTimeMean{strategy}}}{{{row['mean']:.2f}}}\n"
        latex += f"\\DefMacro{{InstrTimeMedian{strategy}}}{{{row['median']:.2f}}}\n"
        latex += f"\\DefMacro{{InstrTimeMax{strategy}}}{{{row['max']:.2f}}}\n"
        latex += f"\\DefMacro{{InstrTimeMin{strategy}}}{{{row['min']:.2f}}}\n"
        latex += f"\\DefMacro{{InstrTimeSum{strategy}}}{{{(row['sum']):.2f}}}\n"

    # 2. End-to-End Time Statistics
    print(f"\n{'='*80}\n2. End-to-End Time Statistics (Table 2)\n{'='*80}")
    e2e_stats = compute_stats(time_data, 'end_to_end_time')
    e2e_stats_display = e2e_stats.copy()
    e2e_stats_display[['mean', 'median', 'max', 'min', 'sum']] = e2e_stats_display[['mean', 'median', 'max', 'min', 'sum']].round(2)
    print(tabulate(e2e_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in e2e_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% End-to-End Time Statistics (Table 2)\n"
        latex += f"\\DefMacro{{E2ETimeMean{strategy}}}{{{row['mean']:.2f}}}\n"
        latex += f"\\DefMacro{{E2ETimeMedian{strategy}}}{{{row['median']:.2f}}}\n"
        latex += f"\\DefMacro{{E2ETimeMax{strategy}}}{{{row['max']:.2f}}}\n"
        latex += f"\\DefMacro{{E2ETimeMin{strategy}}}{{{row['min']:.2f}}}\n"
        latex += f"\\DefMacro{{E2ETimeSum{strategy}}}{{{(row['sum']):.2f}}}\n"

    # 3. Total Instrumentation and Test Time per Strategy
    print(f"\n{'='*80}\n3. Total Instrumentation and Test Time per Strategy (Bar Plot 1)\n{'='*80}")
    time_sums = time_data.groupby('type_project')[['time_instrumentation', 'test_duration']].sum().reset_index()
    time_sums_display = time_sums.copy()
    time_sums_display[['time_instrumentation', 'test_duration']] = time_sums_display[['time_instrumentation', 'test_duration']].round(2)
    print(tabulate(time_sums_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in time_sums.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Instrumentation and Test Time per Strategy (Bar Plot 1)\n"
        latex += f"\\DefMacro{{TotalInstrTime{strategy}}}{{{row['time_instrumentation']}}}\n"
        latex += f"\\DefMacro{{TotalTestTime{strategy}}}{{{row['test_duration']}}}\n"

    # 4. Total Unique Violations Detected per Strategy
    print(f"\n{'='*80}\n4. Total Unique Violations Detected per Strategy (Bar Plot 2)\n{'='*80}")
    viol_data = compute_unique_violations(viol_data)
    viol_sums = viol_data.groupby('type_project')[['unique_violations_count']].sum().reset_index()
    print(tabulate(viol_sums, headers='keys', tablefmt='psql', showindex=False))
    for _, row in viol_sums.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Unique Violations Detected per Strategy (Bar Plot 2)\n"
        latex += f"\\DefMacro{{TotalUniqueViolations{strategy}}}{{{row['unique_violations_count']}}}\n"
        latex += f"\\DefMacro{{text_TotalUniqueViolations{strategy}}}{{{row['unique_violations_count']:,}}}\n"

    # 5. Total Passed and Failed Tests per Strategy
    print(f"\n{'='*80}\n5. Total Passed and Failed Tests per Strategy (Bar Plot 3)\n{'='*80}")
    pass_fail_sums = pass_fail_data.groupby('type_project')[['passed', 'failed']].sum().reset_index()
    print(tabulate(pass_fail_sums, headers='keys', tablefmt='psql', showindex=False))
    for _, row in pass_fail_sums.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Passed and Failed Tests per Strategy (Bar Plot 3)\n"
        latex += f"\\DefMacro{{TotalPassedTests{strategy}}}{{{int(row['passed'])}}}\n"
        latex += f"\\DefMacro{{TotalFailedTests{strategy}}}{{{int(row['failed'])}}}\n"
        latex += f"\\DefMacro{{text_TotalFailedTests{strategy}}}{{{int(row['failed']):,}}}\n"

    def extract_unique_paths_from_df(df):
        print('2 df length', len(df))
        df_curse = df[df["type_project"] == "curse"]
        unique_paths = set()
        for value in df_curse["violations_by_location"].dropna():
            for entry in value.split(';'):
                if '=' in entry:
                    path = entry.split('=')[0].strip()
                    unique_paths.add(path)
        return unique_paths

    # Additional Metrics
    print(f"\n{'='*80}\nAdditional Metrics\n{'='*80}")
    unique_paths_unfiltered = len(extract_unique_paths_from_df(data))
    unique_paths_filtered = len(extract_unique_paths_from_df(time_data))
    num_projects_viol_data = viol_data['project'].nunique()
    total_violations_non_filtered = get_all_unique_violations(data)
    print(f"Violation Count (Unfiltered, Curse Only): {unique_paths_unfiltered:,}")
    print(f"Violation Count (Filtered, Curse Only): {unique_paths_filtered:,}")
    print(f"Number of Projects for Violation Data: {num_projects_viol_data:,}")
    print(f"Total Unique Violations (Non-Filtered): {total_violations_non_filtered:,}\n")

    latex += f"\\DefMacro{{ProjectCountFilteredRQ2}}{{{num_projects_viol_data:,}}}\n"
    latex += f"\\DefMacro{{TotalViolationsNonFiltered}}{{{total_violations_non_filtered:,}}}\n"

    # 6. Total Violations by Origin per Strategy (Non-Filtered)
    print(f"\n{'='*80}\n6. Total Violations by Origin per Strategy NonFiltered (Bar Plot 4)\n{'='*80}")
    violations_by_origin = parse_violations_by_location(data)
    print(tabulate(violations_by_origin, headers='keys', tablefmt='psql', showindex=False))
    for _, row in violations_by_origin.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations by Origin per Strategy NonFiltered (Bar Plot 4)\n"
        latex += f"\\DefMacro{{TotalViolationsPythonSource{strategy}NonFiltered}}{{{int(row['python_source'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsSitePackages{strategy}NonFiltered}}{{{int(row['site_packages'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsProjectUnderTest{strategy}NonFiltered}}{{{int(row['project_under_test'])}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsPythonSource{strategy}NonFiltered}}{{{int(row['python_source']):,}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsSitePackages{strategy}NonFiltered}}{{{int(row['site_packages']):,}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsProjectUnderTest{strategy}NonFiltered}}{{{int(row['project_under_test']):,}}}\n"

    # 7. Total Violations by Origin per Strategy
    print(f"\n{'='*80}\n7. Total Violations by Origin per Strategy (Bar Plot 5)\n{'='*80}")
    violations_by_origin = parse_violations_by_location(viol_data)
    print(tabulate(violations_by_origin, headers='keys', tablefmt='psql', showindex=False))
    for _, row in violations_by_origin.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations by Origin per Strategy (Bar Plot 5)\n"
        latex += f"\\DefMacro{{TotalViolationsPythonSource{strategy}}}{{{int(row['python_source'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsSitePackages{strategy}}}{{{int(row['site_packages'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsProjectUnderTest{strategy}}}{{{int(row['project_under_test'])}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsPythonSource{strategy}}}{{{int(row['python_source']):,}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsSitePackages{strategy}}}{{{int(row['site_packages']):,}}}\n"
        latex += f"\\DefMacro{{text_TotalViolationsProjectUnderTest{strategy}}}{{{int(row['project_under_test']):,}}}\n"

    # 8. Fastest Strategy per Percentile
    print(f"\n{'='*80}\n8. Fastest Strategy per Percentile (Bar Plot 6)\n{'='*80}")
    fastest_counts, percentile_bins = compute_fastest_strategy_per_percentile(time_data, violation_strategies, 'end_to_end_time')
    print(tabulate(fastest_counts, headers='keys', tablefmt='psql', showindex=False))
    for _, row in fastest_counts.iterrows():
        bin_label = row['percentile_bin']
        latex += f"\n% Number of Projects Where Each Strategy is Fastest per Percentile (Bar Plot 6)\n"
        for strategy in violation_strategies:
            strategy_formatted = format_macro_name(strategy)
            value = int(row[strategy]) if strategy in row else 0
            latex += f"\\DefMacro{{ProjectsFastest{strategy_formatted}{bin_label}}}{{{value}}}\n"

    # 9. Instrumentation Time per Strategy (Box Plot 1)
    print(f"\n{'='*80}\n9. Instrumentation Time per Strategy (Box Plot 1)\n{'='*80}")
    instr_box_stats = compute_box_plot_stats(time_data, 'time_instrumentation', strategies)
    instr_box_stats_display = instr_box_stats.copy()
    instr_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = instr_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(instr_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in instr_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Instrumentation Time per Strategy (Box Plot 1)\n"
        latex += f"\\DefMacro{{InstrTime{strategy}LowerWhisker}}{{{row['lower_whisker']}}}\n"
        latex += f"\\DefMacro{{InstrTime{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{InstrTime{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{InstrTime{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{InstrTime{strategy}UpperWhisker}}{{{row['upper_whisker']}}}\n"

    # 10. Test Duration per Strategy (Box Plot 2)
    print(f"\n{'='*80}\n10. Test Duration per Strategy (Box Plot 2)\n{'='*80}")
    test_box_stats = compute_box_plot_stats(time_data, 'test_duration', strategies)
    test_box_stats_display = test_box_stats.copy()
    test_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = test_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(test_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in test_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Test Duration per Strategy (Box Plot 2)\n"
        latex += f"\\DefMacro{{TestDuration{strategy}LowerWhisker}}{{{row['lower_whisker']}}}\n"
        latex += f"\\DefMacro{{TestDuration{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{TestDuration{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{TestDuration{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{TestDuration{strategy}UpperWhisker}}{{{row['upper_whisker']}}}\n"

    # 11. End-to-End Time per Strategy (Box Plot 3)
    print(f"\n{'='*80}\n11. End-to-End Time per Strategy (Box Plot 3)\n{'='*80}")
    e2e_box_stats = compute_box_plot_stats(time_data, 'end_to_end_time', strategies)
    e2e_box_stats_display = e2e_box_stats.copy()
    e2e_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = e2e_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(e2e_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in e2e_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% End-to-End Time per Strategy (Box Plot 3)\n"
        latex += f"\\DefMacro{{E2ETime{strategy}LowerWhisker}}{{{row['lower_whisker']}}}\n"
        latex += f"\\DefMacro{{E2ETime{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{E2ETime{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{E2ETime{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{E2ETime{strategy}UpperWhisker}}{{{row['upper_whisker']}}}\n"

    # 12. Total Violations per Strategy (Box Plot 4)
    print(f"\n{'='*80}\n12. Total Violations per Strategy (Box Plot 4)\n{'='*80}")
    viol_box_stats = compute_box_plot_stats(viol_data, 'total_violations', violation_strategies)
    viol_box_stats_display = viol_box_stats.copy()
    viol_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = viol_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(viol_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in viol_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations per Strategy (Box Plot 4)\n"
        latex += f"\\DefMacro{{TotalViolations{strategy}LowerWhisker}}{{{row['lower_whisker']}}}\n"
        latex += f"\\DefMacro{{TotalViolations{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{TotalViolations{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{TotalViolations{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{TotalViolations{strategy}UpperWhisker}}{{{row['upper_whisker']}}}\n"

    # 13. Passed Tests per Strategy (Box Plot 5)
    print(f"\n{'='*80}\n13. Passed Tests per Strategy (Box Plot 5)\n{'='*80}")
    pass_box_stats = compute_box_plot_stats(pass_fail_data, 'passed', strategies)
    pass_box_stats_display = pass_box_stats.copy()
    pass_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = pass_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(pass_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in pass_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Passed Tests per Strategy (Box Plot 5)\n"
        latex += f"\\DefMacro{{PassedTests{strategy}LowerWhisker}}{{{int(row['lower_whisker'])}}}\n"
        latex += f"\\DefMacro{{PassedTests{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{PassedTests{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{PassedTests{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{PassedTests{strategy}UpperWhisker}}{{{int(row['upper_whisker'])}}}\n"

    # 14. Failed Tests per Strategy (Box Plot 6)
    print(f"\n{'='*80}\n14. Failed Tests per Strategy (Box Plot 6)\n{'='*80}")
    fail_box_stats = compute_box_plot_stats(pass_fail_data, 'failed', strategies)
    fail_box_stats_display = fail_box_stats.copy()
    fail_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = fail_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(fail_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in fail_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Failed Tests per Strategy (Box Plot 6)\n"
        latex += f"\\DefMacro{{FailedTests{strategy}LowerWhisker}}{{{int(row['lower_whisker'])}}}\n"
        latex += f"\\DefMacro{{FailedTests{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{FailedTests{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{FailedTests{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{FailedTests{strategy}UpperWhisker}}{{{int(row['upper_whisker'])}}}\n"

    # 15. Violations by Origin per Strategy (Box Plot 7)
    print(f"\n{'='*80}\n15. Violations by Origin per Strategy (Box Plot 7)\n{'='*80}")
    viol_origin_box_stats = compute_violations_by_origin_box_plot_stats(viol_data, violation_strategies)
    viol_origin_box_stats_display = viol_origin_box_stats.copy()
    viol_origin_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']] = viol_origin_box_stats_display[['lower_whisker', 'lower_quartile', 'median', 'upper_quartile', 'upper_whisker']].round(2)
    print(tabulate(viol_origin_box_stats_display, headers='keys', tablefmt='psql', showindex=False))
    for _, row in viol_origin_box_stats.iterrows():
        strategy = format_macro_name(row['type_project'])
        origin = row['origin'].capitalize().replace('_', '')
        latex += f"\n% Violations by Origin per Strategy (Box Plot 7)\n"
        latex += f"\\DefMacro{{Violations{origin}{strategy}LowerWhisker}}{{{int(row['lower_whisker'])}}}\n"
        latex += f"\\DefMacro{{Violations{origin}{strategy}LowerQuartile}}{{{row['lower_quartile']}}}\n"
        latex += f"\\DefMacro{{Violations{origin}{strategy}Median}}{{{row['median']}}}\n"
        latex += f"\\DefMacro{{Violations{origin}{strategy}UpperQuartile}}{{{row['upper_quartile']}}}\n"
        latex += f"\\DefMacro{{Violations{origin}{strategy}UpperWhisker}}{{{int(row['upper_whisker'])}}}\n"

    # 16. Total Violations by Type per Strategy (Projects where Monkey Patching is Fastest) (Bar Plot 7)
    print(f"\n{'='*80}\n16. Total Violations by Type per Strategy (Projects where Monkey Patching is Fastest) (Bar Plot 7)\n{'='*80}")
    monkey_patching_projects = fastest_df[fastest_df['fastest_strategy'] == 'monkey patching']['project'].tolist()
    viol_data_monkey = viol_data[viol_data['project'].isin(monkey_patching_projects)]
    violations_by_type_monkey = parse_violations_by_type(viol_data_monkey)
    print(tabulate(violations_by_type_monkey, headers='keys', tablefmt='psql', showindex=False))
    for _, row in violations_by_type_monkey.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations by Type per Strategy (Projects where Monkey Patching is Fastest) (Bar Plot 7)\n"
        latex += f"\\DefMacro{{TotalViolationsBuiltinMonkeyFastest{strategy}}}{{{int(row['builtin'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsNonBuiltinMonkeyFastest{strategy}}}{{{int(row['non_builtin'])}}}\n"

    # 17. Total Violations by Type per Strategy (Projects where Curse is Fastest) (Bar Plot 8)
    print(f"\n{'='*80}\n17. Total Violations by Type per Strategy (Projects where Curse is Fastest) (Bar Plot 8)\n{'='*80}")
    curse_projects = fastest_df[fastest_df['fastest_strategy'] == 'curse']['project'].tolist()
    viol_data_curse = viol_data[viol_data['project'].isin(curse_projects)]
    violations_by_type_curse = parse_violations_by_type(viol_data_curse)
    print(tabulate(violations_by_type_curse, headers='keys', tablefmt='psql', showindex=False))
    for _, row in violations_by_type_curse.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations by Type per Strategy (Projects where Curse is Fastest) (Bar Plot 8)\n"
        latex += f"\\DefMacro{{TotalViolationsBuiltinCurseFastest{strategy}}}{{{int(row['builtin'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsNonBuiltinCurseFastest{strategy}}}{{{int(row['non_builtin'])}}}\n"

    # 18. Total Violations by Type per Strategy (Projects where AST is Fastest) (Bar Plot 9)
    print(f"\n{'='*80}\n18. Total Violations by Type per Strategy (Projects where AST is Fastest) (Bar Plot 9)\n{'='*80}")
    ast_projects = fastest_df[fastest_df['fastest_strategy'] == 'ast']['project'].tolist()
    viol_data_ast = viol_data[viol_data['project'].isin(ast_projects)]
    violations_by_type_ast = parse_violations_by_type(viol_data_ast)
    print(tabulate(violations_by_type_ast, headers='keys', tablefmt='psql', showindex=False))
    for _, row in violations_by_type_ast.iterrows():
        strategy = format_macro_name(row['type_project'])
        latex += f"\n% Total Violations by Type per Strategy (Projects where AST is Fastest) (Bar Plot 9)\n"
        latex += f"\\DefMacro{{TotalViolationsBuiltinASTFastest{strategy}}}{{{int(row['builtin'])}}}\n"
        latex += f"\\DefMacro{{TotalViolationsNonBuiltinASTFastest{strategy}}}{{{int(row['non_builtin'])}}}\n"

    return latex

# Generate and save variables.tex
latex_code = generate_variables_latex()
with open('inst-strategies-plots-variables.tex', 'w') as f:
    f.write(latex_code)

print("\nLaTeX variables generated and saved to 'inst-strategies-plots-variables.tex'.")