import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Parse the mode argument to determine which algorithms to use
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    remaining_args = sys.argv[2:]
    if len(remaining_args) > 0:
        mode = int(remaining_args[0])
        remaining_args = remaining_args[1:]
    else:
        mode = 1
else:
    raise ValueError("File path must be provided as arguments!")

# Determine which algorithms to use based on the mode
if mode == 1:
    algorithms_to_use = ['original', 'D', 'dynapyt', 'dynapyt_libs', 'dylin']
elif mode == 2:
    algorithms_to_use = ['original', 'D', 'dynapyt_libs']
elif mode == 3:
    algorithms_to_use = ['original', 'D', 'dylin']
elif mode == 4:
    algorithms_to_use = ['original', 'D', 'dylin_libs']
else:
    algorithms_to_use = ['original', 'D', 'dynapyt', 'dynapyt_libs', 'dylin', 'dylin_libs']

# Parse --no-details flag for whether to print details
print_details = False # Default to not printing details
if len(remaining_args) > 0:
    if remaining_args[0] == '--details':
        print_details = True
    else:
        raise ValueError("Invalid flag entered!")

# Declare columns for test results
test_columns = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']

# Load the result dataset for the comparison experiment
data = pd.read_csv(file_path)

# Replace 'x' with NaN for relevant test columns
for col in test_columns:
    data[col] = pd.to_numeric(data[col].replace('x', pd.NA), errors='coerce')

# Define success criteria for selected algorithms
success_dict = {}
for algo in algorithms_to_use:
    success_dict[algo] = data[(data['algorithm'] == algo) & (~data[test_columns].isna().any(axis=1))]

# Get the projects where algorithm was successful
success_original = success_dict.get('original', pd.DataFrame())
success_D = success_dict.get('D', pd.DataFrame())
success_dynapyt = success_dict.get('dynapyt', pd.DataFrame())
success_dynapyt_libs = success_dict.get('dynapyt_libs', pd.DataFrame())
success_dylin = success_dict.get('dylin', pd.DataFrame())
success_dylin_libs = success_dict.get('dylin_libs', pd.DataFrame())

# Get the projects where original algorithm was successful
successful_projects = success_original['project'].unique()

# ================================================
# Calculate metrics for the comparison experiment (number of projects with same results)
# ================================================
def calculate_metrics(data, success_original, successful_projects, algorithms_to_use):
    pymop_same = 0
    pymop_different = 0
    pymop_missing = 0
    dynapyt_same = 0
    dynapyt_different = 0
    dynapyt_missing = 0
    dynapyt_libs_same = 0
    dynapyt_libs_different = 0
    dynapyt_libs_missing = 0
    dylin_same = 0
    dylin_different = 0
    dylin_missing = 0
    dylin_libs_same = 0
    dylin_libs_different = 0
    dylin_libs_missing = 0
    projects_with_same_results = []

    for project in successful_projects:
        # Get the test results for the original algorithm
        original_result = success_original[success_original['project'] == project][test_columns].values

        # Compare with D
        if 'D' in algorithms_to_use:
            pymop_result = data[(data['algorithm'] == 'D') & (data['project'] == project)][test_columns].values
            if pymop_result.size and not pd.isna(pymop_result).any():
                if (original_result == pymop_result).all():
                    pymop_same += 1
                else:
                    pymop_different += 1
                    print(f"Pymop different: {project}")
            else:
                pymop_missing += 1
                print(f"Pymop missing: {project}")

        # Compare with DynaPyt
        if 'dynapyt' in algorithms_to_use:
            dynapyt_result = data[(data['algorithm'] == 'dynapyt') & (data['project'] == project)][test_columns].values
            if dynapyt_result.size and not pd.isna(dynapyt_result).any():
                if (original_result == dynapyt_result).all():
                    dynapyt_same += 1
                else:
                    dynapyt_different += 1
                    print(f"Dynapyt different: {project}")
            else:
                dynapyt_missing += 1
                print(f"Dynapyt missing: {project}")

        # Compare with DynaPyt_libs
        if 'dynapyt_libs' in algorithms_to_use:
            dynapyt_libs_result = data[(data['algorithm'] == 'dynapyt_libs') & (data['project'] == project)][test_columns].values
            if dynapyt_libs_result.size and not pd.isna(dynapyt_libs_result).any():
                if (original_result == dynapyt_libs_result).all():
                    dynapyt_libs_same += 1
                else:
                    dynapyt_libs_different += 1
                    print(f"DynaPyt_libs different: {project}")
            else:
                dynapyt_libs_missing += 1
                print(f"DynaPyt_libs missing: {project}")

        # Compare with DyLin
        if 'dylin' in algorithms_to_use:
            dylin_result = data[(data['algorithm'] == 'dylin') & (data['project'] == project)][test_columns].values
            if dylin_result.size and not pd.isna(dylin_result).any():
                if (original_result == dylin_result).all():
                    dylin_same += 1
                else:
                    dylin_different += 1
                    print(f"DyLin different: {project}")
            else:
                dylin_missing += 1
                print(f"DyLin missing: {project}")
        
        # Compare with DyLin_libs
        if 'dylin_libs' in algorithms_to_use:
            dylin_libs_result = data[(data['algorithm'] == 'dylin_libs') & (data['project'] == project)][test_columns].values
            if dylin_libs_result.size and not pd.isna(dylin_libs_result).any():
                if (original_result == dylin_libs_result).all():
                    dylin_libs_same += 1
                else:   
                    dylin_libs_different += 1
                    print(f"Dylin_libs different: {project}")
            else:
                dylin_libs_missing += 1
                print(f"Dylin_libs missing: {project}")

        # Only append to projects_with_same_results if all selected algorithms match original
        all_match = True
        for algo in algorithms_to_use:
            if algo == 'original':
                continue
            algo_result = data[(data['algorithm'] == algo) & (data['project'] == project)][test_columns].values
            if not (algo_result.size and not pd.isna(algo_result).any() and (original_result == algo_result).all()):
                all_match = False
                break
        if all_match and len(algorithms_to_use) > 1:
            projects_with_same_results.append(project)
    return pymop_same, pymop_different, pymop_missing, dynapyt_same, dynapyt_different, dynapyt_missing, dynapyt_libs_same, dynapyt_libs_different, dynapyt_libs_missing, dylin_same, dylin_different, dylin_missing, dylin_libs_same, dylin_libs_different, dylin_libs_missing, projects_with_same_results

# Calculate metrics for the comparison experiment (number of projects with same results)
metrics = calculate_metrics(data, success_original, successful_projects, algorithms_to_use)

# Print results for the comparison experiment (number of projects with same results)
pymop_same, pymop_different, pymop_missing, dynapyt_same, dynapyt_different, dynapyt_missing, dynapyt_libs_same, dynapyt_libs_different, dynapyt_libs_missing, dylin_same, dylin_different, dylin_missing, dylin_libs_same, dylin_libs_different, dylin_libs_missing, projects_with_same_results = metrics
print(f"\nResults for the comparison experiment:")
print()
print ("================================================")
print ("===== Number of projects with same results =====")
print ("================================================")
print()
print(f"Total successful projects (Original): {len(success_original)}")
if 'D' in algorithms_to_use:
    print(f"Pymop - Same results: {pymop_same}, Different results: {pymop_different}, Missing results: {pymop_missing}")
    print(f"pymop - Same percentage: {pymop_same * 100.0 / len(success_original):.1f}%, Different percentage: {pymop_different * 100.0 / len(success_original):.1f}%, Missing percentage: {pymop_missing * 100.0 / len(success_original):.1f}%")
if 'dynapyt' in algorithms_to_use:
    print(f"Dynapyt - Same results: {dynapyt_same}, Different results: {dynapyt_different}, Missing results: {dynapyt_missing}")
    print(f"dynapyt - Same percentage: {dynapyt_same * 100.0 / len(success_original):.1f}%, Different percentage: {dynapyt_different * 100.0 / len(success_original):.1f}%, Missing percentage: {dynapyt_missing * 100.0 / len(success_original):.1f}%")
if 'dynapyt_libs' in algorithms_to_use:
    print(f"DynaPyt_libs - Same results: {dynapyt_libs_same}, Different results: {dynapyt_libs_different}, Missing results: {dynapyt_libs_missing}")
    print(f"DynaPyt_libs - Same percentage: {dynapyt_libs_same * 100.0 / len(success_original):.1f}%, Different percentage: {dynapyt_libs_different * 100.0 / len(success_original):.1f}%, Missing percentage: {dynapyt_libs_missing * 100.0 / len(success_original):.1f}%")
if 'dylin' in algorithms_to_use:
    print(f"DyLin - Same results: {dylin_same}, Different results: {dylin_different}, Missing results: {dylin_missing}")
    print(f"DyLin - Same percentage: {dylin_same * 100.0 / len(success_original):.1f}%, Different percentage: {dylin_different * 100.0 / len(success_original):.1f}%, Missing percentage: {dylin_missing * 100.0 / len(success_original):.1f}%")
if 'dylin_libs' in algorithms_to_use:
    print(f"Dylin_libs - Same results: {dylin_libs_same}, Different results: {dylin_libs_different}, Missing results: {dylin_libs_missing}")
    print(f"Dylin_libs - Same percentage: {dylin_libs_same * 100.0 / len(success_original):.1f}%, Different percentage: {dylin_libs_different * 100.0 / len(success_original):.1f}%, Missing percentage: {dylin_libs_missing * 100.0 / len(success_original):.1f}%")

# Calculate the maximum speed up of the algorithms
if len(algorithms_to_use) <= 3:
    max_speedup = 0
    total_speedup = 0
    for project in projects_with_same_results:
        pymop_time = data[(data['algorithm'] == 'D') & (data['project'] == project)]['end_to_end_time'].values[0]
        tool_time = 0
        for algo in algorithms_to_use:
            if algo == 'original' or algo == 'D':
                continue
            tool_time = data[(data['algorithm'] == algo) & (data['project'] == project)]['end_to_end_time'].values[0]
        try:
            speedup = float(tool_time) / float(pymop_time)
            if speedup > max_speedup:
                max_speedup = speedup
            total_speedup += speedup
        except:
            print(f"Project: {project}, Pymop time: {pymop_time}, Tool time: {tool_time}")
            continue
        print(f"Project: {project}, Pymop time: {pymop_time}, Tool time: {tool_time}, Speedup: {speedup}")
    print(f"Maximum speedup: {max_speedup}")
    print(f"Total speedup: {total_speedup}")
    print(f"Average speedup: {total_speedup / len(projects_with_same_results)}")

# ================================================
# Compare violation locations for projects with same results
# ================================================

# Parse violations by location
def parse_violations_by_location(violations_str):
    if pd.isna(violations_str) or violations_str == 'x':
        return set()
    
    locations = set()
    if violations_str:
        # Split by semicolon and process each location
        parts = violations_str.split(';')
        for part in parts:
            if '=' in part:
                location = part.split('=')[0].strip()
                locations.add(location)
    return locations

def compare_violation_locations(data, projects_with_same_results, algorithms_to_use):
    location_comparison_results = {}
    filtered_location_comparison_results = {}  # For comparison without /usr/lib/python3.10
    
    for algo in ['dynapyt', 'dynapyt_libs', 'dylin', 'dylin_libs']:
        if algo not in algorithms_to_use:
            continue
            
        # Regular comparison results
        same_locations = 0
        pymop_superset = 0
        algo_superset = 0
        different_locations = 0
        total_compared = 0
        different_cases = []
        superset_cases = []  # New list for superset cases
        
        # Filtered comparison results (excluding /usr/lib/python3.10)
        filtered_same_locations = 0
        filtered_pymop_superset = 0
        filtered_algo_superset = 0
        filtered_different_locations = 0
        filtered_total_compared = 0
        filtered_different_cases = []
        filtered_superset_cases = []  # New list for filtered superset cases
        
        for project in projects_with_same_results:
            pymop_data = data[(data['algorithm'] == 'D') & (data['project'] == project)]
            algo_data = data[(data['algorithm'] == algo) & (data['project'] == project)]
            
            if not pymop_data.empty and not algo_data.empty:
                total_compared += 1
                filtered_total_compared += 1
                
                # Regular comparison
                pymop_locations = parse_violations_by_location(pymop_data['violations_by_location'].iloc[0])
                algo_locations = parse_violations_by_location(algo_data['violations_by_location'].iloc[0])

                # Filtered out violations from pythonmop
                pymop_locations = {loc for loc in pymop_locations 
                                 if 'pythonmop' not in loc}
                
                # Filtered comparison - apply different filters based on algorithm
                if algo == 'dynapyt' or algo == 'dylin':
                    # For DynaPyt, exclude both patterns
                    filtered_pymop_locations = {loc for loc in pymop_locations 
                                             if not loc.startswith('/usr/lib/python3.12') 
                                             and 'venv/lib/python3.12/site-packages' not in loc}
                else:  # dynapyt_libs
                    # For DynaPyt_libs, only exclude /usr/lib/python3.10
                    filtered_pymop_locations = {loc for loc in pymop_locations 
                                             if not loc.startswith('/usr/lib/python3.12')}
                
                # Regular comparison logic
                if not pymop_locations and not algo_locations:
                    same_locations += 1
                elif pymop_locations == algo_locations:
                    same_locations += 1
                elif pymop_locations.issuperset(algo_locations):
                    pymop_superset += 1
                    superset_cases.append({
                        'project': project,
                        'type': 'pymop_superset',
                        'additional': pymop_locations - algo_locations
                    })
                elif algo_locations.issuperset(pymop_locations):
                    algo_superset += 1
                    superset_cases.append({
                        'project': project,
                        'type': 'algo_superset',
                        'additional': algo_locations - pymop_locations
                    })
                else:
                    different_locations += 1
                    different_cases.append({
                        'project': project,
                        'pymop_unique': pymop_locations - algo_locations,
                        'algo_unique': algo_locations - pymop_locations
                    })
                
                # Filtered comparison logic
                if not filtered_pymop_locations and not algo_locations:
                    filtered_same_locations += 1
                elif filtered_pymop_locations == algo_locations:
                    filtered_same_locations += 1
                elif filtered_pymop_locations.issuperset(algo_locations):
                    filtered_pymop_superset += 1
                    filtered_superset_cases.append({
                        'project': project,
                        'type': 'pymop_superset',
                        'additional': filtered_pymop_locations - algo_locations
                    })
                elif algo_locations.issuperset(filtered_pymop_locations):
                    filtered_algo_superset += 1
                    filtered_superset_cases.append({
                        'project': project,
                        'type': 'algo_superset',
                        'additional': algo_locations - filtered_pymop_locations
                    })
                else:
                    filtered_different_locations += 1
                    filtered_different_cases.append({
                        'project': project,
                        'pymop_unique': filtered_pymop_locations - algo_locations,
                        'algo_unique': algo_locations - filtered_pymop_locations
                    })
        
        location_comparison_results[algo] = {
            'same_locations': same_locations,
            'pymop_superset': pymop_superset,
            'algo_superset': algo_superset,
            'different_locations': different_locations,
            'total_compared': total_compared,
            'different_cases': different_cases,
            'superset_cases': superset_cases
        }
        
        filtered_location_comparison_results[algo] = {
            'same_locations': filtered_same_locations,
            'pymop_superset': filtered_pymop_superset,
            'algo_superset': filtered_algo_superset,
            'different_locations': filtered_different_locations,
            'total_compared': filtered_total_compared,
            'different_cases': filtered_different_cases,
            'superset_cases': filtered_superset_cases
        }
    
    return location_comparison_results, filtered_location_comparison_results

# Filter projects_with_same_results to only those in selected_projects
filtered_projects_with_same_results = set(projects_with_same_results)

# Find the violation locations for projects with same results and compare them between algorithms
location_comparison_results, filtered_location_comparison_results = compare_violation_locations(data, filtered_projects_with_same_results, algorithms_to_use)

# Print violation location comparison results
print()
print ("========================================================")
print ("===== Violation Location Comparison (project level)=====")
print ("========= For projects with consistent results =========")
print ("========================================================")
print()

print("=> REGULAR COMPARISON (All Violations) <=")

for algo, results in location_comparison_results.items():
    print(f"\nPyMOP vs {algo}:")
    print(f"Total projects compared: {results['total_compared']}")
    if results['total_compared'] > 0:
        print(f"Same number of unique violations: {results['same_locations']} ({results['same_locations']*100.0/results['total_compared']:.1f}%)")
        print(f"PyMOP includes all {algo} unique violations and more: {results['pymop_superset']} ({results['pymop_superset']*100.0/results['total_compared']:.1f}%)")
        print(f"{algo} includes all PyMOP unique violations and more: {results['algo_superset']} ({results['algo_superset']*100.0/results['total_compared']:.1f}%)")
        print(f"Each has unique violations that the other does not have: {results['different_locations']} ({results['different_locations']*100.0/results['total_compared']:.1f}%)")
        
        if print_details:
            # Print superset cases
            if results['pymop_superset'] > 0:
                print("\nCases where PyMOP includes all violations plus more:")
                for case in results['superset_cases']:
                    if case['type'] == 'pymop_superset':
                        print(f"\nProject: {case['project']}")
                        print("Additional violations in PyMOP:")
                        for loc in sorted(case['additional']):
                            print(f"  {loc}")
            
            if results['algo_superset'] > 0:
                print(f"\nCases where {algo} includes all violations plus more:")
                for case in results['superset_cases']:
                    if case['type'] == 'algo_superset':
                        print(f"\nProject: {case['project']}")
                        print(f"Additional violations in {algo}:")
                        for loc in sorted(case['additional']):
                            print(f"  {loc}")
            
            # Print cases with differences on both sides
            if results['different_locations'] > 0:
                print("\nCases where each has unique violations:")
                for case in results['different_cases']:
                    print(f"\nProject: {case['project']}")
                    print("PyMOP unique violations:")
                    for loc in sorted(case['pymop_unique']):
                        print(f"  {loc}")
                    print(f"{algo} unique violations:")
                    for loc in sorted(case['algo_unique']):
                        print(f"  {loc}")

for algo, results in filtered_location_comparison_results.items():
    if algo == 'dynapyt':
        print("\n=> FILTERED COMPARISON (Excluding /usr/lib/python3.10 and venv/lib/python3.10/site-packages from PyMOP) <=")
    else:
        print("\n=> FILTERED COMPARISON (Excluding /usr/lib/python3.10 from PyMOP) <=")
    print(f"\nPyMOP vs {algo}:")
    print(f"Total projects compared: {results['total_compared']}")
    if results['total_compared'] > 0:
        print(f"Same number of unique violations: {results['same_locations']} ({results['same_locations']*100.0/results['total_compared']:.1f}%)")
        print(f"PyMOP includes all {algo} unique violations and more: {results['pymop_superset']} ({results['pymop_superset']*100.0/results['total_compared']:.1f}%)")
        print(f"{algo} includes all PyMOP unique violations and more: {results['algo_superset']} ({results['algo_superset']*100.0/results['total_compared']:.1f}%)")
        print(f"Each has unique violations that the other does not have: {results['different_locations']} ({results['different_locations']*100.0/results['total_compared']:.1f}%)")
        
        if print_details:
            # Print superset cases
            if results['pymop_superset'] > 0:
                print("\nCases where PyMOP includes all violations plus more:")
                for case in results['superset_cases']:
                    if case['type'] == 'pymop_superset':
                        print(f"\nProject: {case['project']}")
                        print("Additional violations in PyMOP:")
                        for loc in sorted(case['additional']):
                            print(f"  {loc}")
            
            if results['algo_superset'] > 0:
                print(f"\nCases where {algo} includes all violations plus more:")
                for case in results['superset_cases']:
                    if case['type'] == 'algo_superset':
                        print(f"\nProject: {case['project']}")
                        print(f"Additional violations in {algo}:")
                        for loc in sorted(case['additional']):
                            print(f"  {loc}")
            
            # Print cases with differences on both sides
            if results['different_locations'] > 0:
                print("\nCases where each has unique violations:")
                for case in results['different_cases']:
                    print(f"\nProject: {case['project']}")
                    print("PyMOP unique violations:")
                    for loc in sorted(case['pymop_unique']):
                        print(f"  {loc}")
                    print(f"{algo} unique violations:")
                    for loc in sorted(case['algo_unique']):
                        print(f"  {loc}")

# ================================================
# Compare performance between algorithms
# ================================================

print()
print ("=========================================")
print ("========= Performance Comparison ========")
print ("=========================================")
print()

# Process timing data
data['time_instrumentation'] = pd.to_numeric(data['time_instrumentation'].replace('x', pd.NA), errors='coerce')
data['time_create_monitor'] = pd.to_numeric(data['time_create_monitor'].replace('x', pd.NA), errors='coerce')
data['test_duration'] = pd.to_numeric(data['test_duration'].replace('x', pd.NA), errors='coerce')
data['end_to_end_time'] = pd.to_numeric(data['end_to_end_time'].replace('x', pd.NA), errors='coerce')
data['inst_and_monitor_time'] = data['time_instrumentation'] + data['time_create_monitor']

# Compare D vs DynaPyt performance (only if both are selected)
if 'D' in algorithms_to_use and 'dynapyt' in algorithms_to_use:
    print(f"\n=> Performance Comparison (D vs DynaPyt) <=")
    # Get projects where both D and DynaPyt have valid times
    valid_projects = data[data['end_to_end_time'].notna() & 
                         data['test_duration'].notna()]['project'].unique()

    # Filter projects_with_same_results excluding specified ones
    filtered_projects_with_same_results = set(projects_with_same_results)

    # Store time differences for each project
    endtoend_differences = []
    test_differences = []
    d_faster_endtoend = 0
    dynapyt_faster_endtoend = 0
    d_faster_test = 0
    dynapyt_faster_test = 0

    # Use only projects with consistent results
    for project in filtered_projects_with_same_results:
        # Ensure project also has valid timing data
        if project in valid_projects:
            d_times = data[(data['algorithm'] == 'D') & (data['project'] == project)]
            dynapyt_times = data[(data['algorithm'] == 'dynapyt') & (data['project'] == project)]
            
            if not d_times.empty and not dynapyt_times.empty:
                # End-to-end time comparison
                d_endtoend = d_times['end_to_end_time'].iloc[0]
                dynapyt_endtoend = dynapyt_times['end_to_end_time'].iloc[0]
                endtoend_diff = abs(d_endtoend - dynapyt_endtoend)
                faster_algo = 'D' if d_endtoend < dynapyt_endtoend else 'DynaPyt'
                endtoend_differences.append((project, endtoend_diff, faster_algo))
                if faster_algo == 'D':
                    d_faster_endtoend += 1
                else:
                    dynapyt_faster_endtoend += 1
                
                # Test duration comparison
                d_test = d_times['test_duration'].iloc[0]
                dynapyt_test = dynapyt_times['test_duration'].iloc[0]
                test_diff = abs(d_test - dynapyt_test)
                faster_algo = 'D' if d_test < dynapyt_test else 'DynaPyt'
                test_differences.append((project, test_diff, faster_algo))
                if faster_algo == 'D':
                    d_faster_test += 1
                else:
                    dynapyt_faster_test += 1

    # Sort by time difference
    endtoend_differences.sort(key=lambda x: x[1], reverse=True)
    test_differences.sort(key=lambda x: x[1], reverse=True)

    # Print the results
    print(f"\nNumber of projects where D is faster (end-to-end): {d_faster_endtoend}")
    print(f"Number of projects where DynaPyt is faster (end-to-end): {dynapyt_faster_endtoend}")
    print(f"Number of projects where D is faster (test duration): {d_faster_test}")
    print(f"Number of projects where DynaPyt is faster (test duration): {dynapyt_faster_test}")

    # Print the top 10 projects where D is faster (end-to-end, vs DynaPyt_libs)
    if print_details:
        print("\nEnd-to-end time differences (top 10):")
        for i, (project, diff, faster) in enumerate(endtoend_differences[:10], 1):
            print(f"{i}. Project: {project}")
            print(f"   Time difference: {diff:.2f} seconds")
            print(f"   Faster algorithm: {faster}")
            
        print("\nTest duration differences (top 10):")
        for i, (project, diff, faster) in enumerate(test_differences[:10], 1):
            print(f"{i}. Project: {project}")
            print(f"   Time difference: {diff:.2f} seconds")
            print(f"   Faster algorithm: {faster}")

# Compare D vs DynaPyt_libs performance (only if both are selected)
if 'D' in algorithms_to_use and 'dynapyt_libs' in algorithms_to_use:
    print(f"\n=> Performance Comparison (D vs DynaPyt_libs) <=")
    # Get projects where both D and DynaPyt_libs have valid times
    valid_projects = data[data['end_to_end_time'].notna() & 
                         data['test_duration'].notna()]['project'].unique()

    # Filter projects_with_same_results excluding specified ones
    filtered_projects_with_same_results = set(projects_with_same_results)

    # Store time differences for each project
    endtoend_differences_libs = []
    test_differences_libs = []
    d_faster_endtoend_libs = 0
    dynapyt_libs_faster_endtoend = 0
    d_faster_test_libs = 0
    dynapyt_libs_faster_test = 0

    # Use only projects with consistent results
    for project in filtered_projects_with_same_results:
        if project in valid_projects:
            d_times = data[(data['algorithm'] == 'D') & (data['project'] == project)]
            dynapyt_libs_times = data[(data['algorithm'] == 'dynapyt_libs') & (data['project'] == project)]
            
            if not d_times.empty and not dynapyt_libs_times.empty:
                # End-to-end time comparison
                d_endtoend = d_times['end_to_end_time'].iloc[0]
                dynapyt_libs_endtoend = dynapyt_libs_times['end_to_end_time'].iloc[0]
                endtoend_diff = abs(d_endtoend - dynapyt_libs_endtoend)
                faster_algo = 'D' if d_endtoend < dynapyt_libs_endtoend else 'DynaPyt_libs'
                endtoend_differences_libs.append((project, endtoend_diff, faster_algo))
                if faster_algo == 'D':
                    d_faster_endtoend_libs += 1
                else:
                    dynapyt_libs_faster_endtoend += 1
                
                # Test duration comparison
                d_test = d_times['test_duration'].iloc[0]
                dynapyt_libs_test = dynapyt_libs_times['test_duration'].iloc[0]
                test_diff = abs(d_test - dynapyt_libs_test)
                faster_algo = 'D' if d_test < dynapyt_libs_test else 'DynaPyt_libs'
                test_differences_libs.append((project, test_diff, faster_algo))
                if faster_algo == 'D':
                    d_faster_test_libs += 1
                else:
                    dynapyt_libs_faster_test += 1

    # Sort by time difference
    endtoend_differences_libs.sort(key=lambda x: x[1], reverse=True)
    test_differences_libs.sort(key=lambda x: x[1], reverse=True)

    # Print the results
    print(f"\nNumber of projects where D is faster (end-to-end, vs DynaPyt_libs): {d_faster_endtoend_libs}")
    print(f"Number of projects where DynaPyt_libs is faster (end-to-end): {dynapyt_libs_faster_endtoend}")
    print(f"Number of projects where D is faster (test duration, vs DynaPyt_libs): {d_faster_test_libs}")
    print(f"Number of projects where DynaPyt_libs is faster (test duration): {dynapyt_libs_faster_test}")

    # Print the top 10 projects where D is faster (end-to-end, vs DynaPyt_libs)
    if print_details:
        print("\nEnd-to-end time differences (top 10, vs DynaPyt_libs):")
        for i, (project, diff, faster) in enumerate(endtoend_differences_libs[:10], 1):
            print(f"{i}. Project: {project}")
            print(f"   Time difference: {diff:.2f} seconds")
            print(f"   Faster algorithm: {faster}")

        print("\nTest duration differences (top 10, vs DynaPyt_libs):")
        for i, (project, diff, faster) in enumerate(test_differences_libs[:10], 1):
            print(f"{i}. Project: {project}")
            print(f"   Time difference: {diff:.2f} seconds")
            print(f"   Faster algorithm: {faster}")

# ================================================
# Violation-level comparison
# ================================================

# Filter projects_with_same_results excluding specified ones
filtered_projects_with_same_results = set(projects_with_same_results) # & set(selected_projects)

def violation_level_comparison(data, projects_with_same_results, pymop_algo, dynapyt_algo, filter_type=None):
    pymop_violations = set()
    dynapyt_violations = set()
    shared_violations = set()
    pymop_only = set()
    dynapyt_only = set()
    
    # Compare violation locations between algorithms for each project
    for project in projects_with_same_results:
        # Get the data for the two algorithms
        pymop_data = data[(data['algorithm'] == pymop_algo) & (data['project'] == project)]
        dynapyt_data = data[(data['algorithm'] == dynapyt_algo) & (data['project'] == project)]

        # If one of the algorithms has no data, skip the project
        if pymop_data.empty or dynapyt_data.empty:
            continue

        # Parse the violations by location
        pymop_locs = parse_violations_by_location(pymop_data['violations_by_location'].iloc[0])
        dynapyt_locs = parse_violations_by_location(dynapyt_data['violations_by_location'].iloc[0])

        # Filtered out violations from pythonmop
        pymop_locs = {loc for loc in pymop_locs 
                     if 'pythonmop' not in loc}

        # Filtering logic
        if filter_type == 'dynapyt' or filter_type == 'dylin':
            pymop_locs = {loc for loc in pymop_locs if not loc.startswith('/usr/lib/python3.12') and 'venv/lib/python3.12/site-packages' not in loc}
        elif filter_type == 'dynapyt_libs' or filter_type == 'dylin_libs':
            pymop_locs = {loc for loc in pymop_locs if not loc.startswith('/usr/lib/python3.12')}

        # Aggregate the violations
        pymop_violations.update(pymop_locs)
        dynapyt_violations.update(dynapyt_locs)

        # Calculate the shared and unique violations
        shared_violations = pymop_violations & dynapyt_violations

    # Calculate the unique violations
    pymop_only = pymop_violations - dynapyt_violations
    dynapyt_only = dynapyt_violations - pymop_violations

    return pymop_only, dynapyt_only, shared_violations

print()
print ("==========================================================")
print ("===== Violation Location Comparison (violation level)=====")
print ("========== For projects with consistent results ==========")
print ("==========================================================")
print()

print("=> REGULAR COMPARISON (All Violations) <=")

# Run the violation-level comparison for each algorithm
for algo in ['dynapyt', 'dynapyt_libs', 'dylin', 'dylin_libs']:
    # Skip if the algorithm is not in the list of algorithms to use
    if algo not in algorithms_to_use:
        continue

    # Print the results for all violations
    pymop_only, dynapyt_only, shared = violation_level_comparison(data, filtered_projects_with_same_results, 'D', algo)
    print(f"\nPyMOP vs {algo}:")
    print(f"Violations only in PyMOP: {len(pymop_only)}")
    print(f"Violations only in {algo}: {len(dynapyt_only)}")
    print(f"Violations shared: {len(shared)}")

    # Print the examples
    if print_details:
        print("\nDetailed violations for each group of violations:")
        print("  Only PyMOP:")
        for loc in list(pymop_only):
            print(f"    {loc}")
        print(f"  Only {algo}:")
        for loc in list(dynapyt_only):
            print(f"    {loc}")
        print("  Shared:")
        for loc in list(shared):
            print(f"    {loc}")

for algo in ['dynapyt', 'dynapyt_libs', 'dylin', 'dylin_libs']:
    if (algo == 'dynapyt' and 'dynapyt' in algorithms_to_use) or (algo == 'dylin' and 'dylin' in algorithms_to_use):
        print("\n=> FILTERED COMPARISON (Excluding /usr/lib/python3.12 and venv/lib/python3.12/site-packages from PyMOP) <=")
    elif (algo == 'dynapyt_libs' and 'dynapyt_libs' in algorithms_to_use) or (algo == 'dylin_libs' and 'dylin_libs' in algorithms_to_use):
        print("\n=> FILTERED COMPARISON (Excluding /usr/lib/python3.12 from PyMOP) <=")
    else:
        continue

    # Print the results for filtered violations (excluding /usr/lib/python3.12 and venv/lib/python3.12/site-packages from PyMOP)
    print(f"\nPyMOP vs {algo}:")
    pymop_only_f, dynapyt_only_f, shared_f = violation_level_comparison(data, filtered_projects_with_same_results, 'D', algo, filter_type=algo)
    print(f"Filtered violations only in PyMOP: {len(pymop_only_f)}")
    print(f"Filtered violations only in {algo}: {len(dynapyt_only_f)}")
    print(f"Filtered violations shared: {len(shared_f)}")

    # Print the examples
    if print_details:
        print("\nDetailed violations for each group of violations:")
        print("  Only PyMOP:")
        for loc in sorted(list(pymop_only_f)):
            print(f"    {loc}")
        print(f"  Only {algo}:")
        for loc in sorted(list(dynapyt_only_f)):
            print(f"    {loc}")
        print("  Shared:")
        for loc in sorted(list(shared_f)):
            print(f"    {loc}")

# Print the number of projects used for analysis
print(f"\nNumber of projects with consistent results: {len(filtered_projects_with_same_results)}")

# # After metrics are calculated, write projects where D is consistent with original to a txt file
# projects_D_consistent = []
# for project in successful_projects:
#     original_result = success_original[success_original['project'] == project][test_columns].values
#     pymop_result = data[(data['algorithm'] == 'D') & (data['project'] == project)][test_columns].values
#     if pymop_result.size and not pd.isna(pymop_result).any():
#         if (original_result == pymop_result).all():
#             projects_D_consistent.append(project)

# with open('projects_D_consistent.txt', 'w') as f:
#     for project in projects_D_consistent:
#         f.write(f"{project}\n")