import pandas as pd
import numpy as np


# Load the data
data = pd.read_csv('gc_results.csv')

# Replace 'x' with NaN for relevant columns
columns_to_numeric = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']
for col in columns_to_numeric:
    data[col] = pd.to_numeric(data[col].replace('x', pd.NA), errors='coerce')

# Define success criteria
success_original = data[(data['type_project'] == 'original') & (~data[columns_to_numeric].isna().any(axis=1))]
success_pymop_no_gc = data[(data['type_project'] == 'pymop_no_gc') & (~data[columns_to_numeric].isna().any(axis=1))]
success_pymop_gc = data[(data['type_project'] == 'pymop_gc') & (~data[columns_to_numeric].isna().any(axis=1))]

# Get the projects where original algorithm was successful
successful_projects = success_original['project'].unique()

# Calculate metrics
columns_to_compare = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed']

def calculate_metrics(data, success_original, successful_projects):
    pymop_no_gc_same = 0
    pymop_no_gc_different = 0
    pymop_no_gc_missing = 0
    pymop_gc_same = 0
    pymop_gc_different = 0
    pymop_gc_missing = 0
    projects_with_same_results = []

    for project in successful_projects:
        original_result = success_original[success_original['project'] == project][columns_to_compare].values
        
        pymop_no_gc_result = data[(data['type_project'] == 'pymop_no_gc') & (data['project'] == project)][columns_to_compare].values
        if pymop_no_gc_result.size and not pd.isna(pymop_no_gc_result).any():
            if (original_result == pymop_no_gc_result).all():
                pymop_no_gc_same += 1
            else:
                pymop_no_gc_different += 1
                print(f"Pymop with no gc different: {project}")
        else:
            pymop_no_gc_missing += 1
            print(f"Pymop with no gc missing: {project}")
        
        pymop_gc_result = data[(data['type_project'] == 'pymop_gc') & (data['project'] == project)][columns_to_compare].values
        if pymop_gc_result.size and not pd.isna(pymop_gc_result).any():
            if (original_result == pymop_gc_result).all():
                pymop_gc_same += 1
            else:
                pymop_gc_different += 1
                print(f"Pymop with gc different: {project}")
        else:
            pymop_gc_missing += 1
            print(f"Pymop with gc missing: {project}")
        
        if pymop_no_gc_result.size and pymop_gc_result.size and not pd.isna(pymop_no_gc_result).any() and not pd.isna(pymop_gc_result).any():
            if (original_result == pymop_no_gc_result).all() and (original_result == pymop_gc_result).all():
                projects_with_same_results.append(project)
    
    return pymop_no_gc_same, pymop_no_gc_different, pymop_no_gc_missing, pymop_gc_same, pymop_gc_different, pymop_gc_missing, projects_with_same_results

# Calculate metrics
metrics = calculate_metrics(data, success_original, successful_projects)

# Print results
pymop_no_gc_same, pymop_no_gc_different, pymop_no_gc_missing, pymop_gc_same, pymop_gc_different, pymop_gc_missing, projects_with_same_results = metrics
print(f"\nResults:")
print(f"Total successful projects (Original): {len(success_original)}")
print(f"Pymop without gc - Same results: {pymop_no_gc_same}, Different results: {pymop_no_gc_different}, Missing results: {pymop_no_gc_missing}")
print(f"pymop without gc - Same percentage: {pymop_no_gc_same * 100.0 / len(success_original):.1f}%, Different percentage: {pymop_no_gc_different * 100.0 / len(success_original):.1f}%, Missing percentage: {pymop_no_gc_missing * 100.0 / len(success_original):.1f}%")
print(f"Pymop with gc - Same results: {pymop_gc_same}, Different results: {pymop_gc_different}, Missing results: {pymop_gc_missing}")
print(f"Pymop with gc - Same percentage: {pymop_gc_same * 100.0 / len(success_original):.1f}%, Different percentage: {pymop_gc_different * 100.0 / len(success_original):.1f}%, Missing percentage: {pymop_gc_missing * 100.0 / len(success_original):.1f}%")

# Process timing data
data['time_instrumentation'] = pd.to_numeric(data['time_instrumentation'].replace('x', pd.NA), errors='coerce')
data['time_create_monitor'] = pd.to_numeric(data['time_create_monitor'].replace('x', pd.NA), errors='coerce')
data['test_duration'] = pd.to_numeric(data['test_duration'].replace('x', pd.NA), errors='coerce')
data['end_to_end_time'] = pd.to_numeric(data['end_to_end_time'].replace('x', pd.NA), errors='coerce')
data['inst_and_monitor_time'] = data['time_instrumentation'] + data['time_create_monitor']
data.loc[data['algorithm'] == 'D', 'test_duration'] = data['end_to_end_time'] - data['inst_and_monitor_time']

# Compare D vs DynaPyt performance
print(f"\nPerformance Comparison:")

# Get projects where both D and DynaPyt have valid times
valid_projects = data[data['end_to_end_time'].notna() & 
                     data['test_duration'].notna()]['project'].unique()

# Filter projects_with_same_results excluding specified ones
filtered_projects_with_same_results = set(projects_with_same_results)

# Store time differences for each project
endtoend_differences = []
test_differences = []

pymop_no_gc_faster_endtoend = 0
pymop_gc_faster_endtoend = 0
pymop_no_gc_faster_test = 0
pymop_gc_faster_test = 0

# Use only projects with consistent results
for project in filtered_projects_with_same_results:
    # Ensure project also has valid timing data
    if project in valid_projects:
        pymop_no_gc_times = data[(data['type_project'] == 'pymop_no_gc') & (data['project'] == project)]
        pymop_gc_times = data[(data['type_project'] == 'pymop_gc') & (data['project'] == project)]
        
        if not pymop_no_gc_times.empty and not pymop_gc_times.empty:
            # End-to-end time comparison
            pymop_no_gc_endtoend = pymop_no_gc_times['end_to_end_time'].iloc[0]
            pymop_gc_endtoend = pymop_gc_times['end_to_end_time'].iloc[0]
            endtoend_diff = abs(pymop_no_gc_endtoend - pymop_gc_endtoend)
            faster_algo = 'Pymop without gc' if pymop_no_gc_endtoend < pymop_gc_endtoend else 'Pymop with gc'
            endtoend_differences.append((project, endtoend_diff, faster_algo))
            if faster_algo == 'Pymop without gc':
                pymop_no_gc_faster_endtoend += 1
            else:
                pymop_gc_faster_endtoend += 1
            
            # Test duration comparison
            pymop_no_gc_test = pymop_no_gc_times['test_duration'].iloc[0]
            pymop_gc_test = pymop_gc_times['test_duration'].iloc[0]
            test_diff = abs(pymop_no_gc_test - pymop_gc_test)
            faster_algo = 'Pymop without gc' if pymop_no_gc_test < pymop_gc_test else 'Pymop with gc'
            test_differences.append((project, test_diff, faster_algo))
            if faster_algo == 'Pymop without gc':
                pymop_no_gc_faster_test += 1
            else:
                pymop_gc_faster_test += 1

# Sort by time difference
endtoend_differences.sort(key=lambda x: x[1], reverse=True)
test_differences.sort(key=lambda x: x[1], reverse=True)

print(f"\nNumber of projects where Pymop without gc is faster (end-to-end): {pymop_no_gc_faster_endtoend}")
print(f"Number of projects where Pymop with gc is faster (end-to-end): {pymop_gc_faster_endtoend}")
print(f"Number of projects where Pymop without gc is faster (test duration): {pymop_no_gc_faster_test}")
print(f"Number of projects where Pymop with gc is faster (test duration): {pymop_gc_faster_test}")

# Write Macros for the research paper
with open('gc_comparison_macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{gc_comparison_macros_total_projects}}{{{len(filtered_projects_with_same_results)}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_endtoend_projects}}{{{pymop_no_gc_faster_endtoend}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_endtoend_projects}}{{{pymop_gc_faster_endtoend}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_test_projects}}{{{pymop_no_gc_faster_test}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_test_projects}}{{{pymop_gc_faster_test}}}\n")

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

# Count projects by 0.1s threshold for end-to-end time
gc_faster_01 = 0
no_gc_faster_01 = 0
same_speed_01 = 0
gc_faster_diffs = []
no_gc_faster_diffs = []

# Add lists to store project names
projects_gc_faster_01 = []
projects_no_gc_faster_01 = []
for project, diff, faster in endtoend_differences:
    pymop_no_gc_endtoend = data[(data['type_project'] == 'pymop_no_gc') & (data['project'] == project)]['end_to_end_time'].iloc[0]
    pymop_gc_endtoend = data[(data['type_project'] == 'pymop_gc') & (data['project'] == project)]['end_to_end_time'].iloc[0]
    if pymop_gc_endtoend + 0.5 < pymop_no_gc_endtoend:
        gc_faster_01 += 1
        gc_faster_diffs.append(pymop_no_gc_endtoend - pymop_gc_endtoend)
        projects_gc_faster_01.append(project)
    elif pymop_no_gc_endtoend + 0.5 < pymop_gc_endtoend:
        no_gc_faster_01 += 1    
        no_gc_faster_diffs.append(pymop_gc_endtoend - pymop_no_gc_endtoend)
        projects_no_gc_faster_01.append(project)
    else:
        same_speed_01 += 1

print(f"\n[End-to-End 0.5s threshold]")
print(f"Projects where pymop_gc is faster than pymop_no_gc by >0.5s: {gc_faster_01}")
if gc_faster_diffs:
    print(f"  Max diff: {np.max(gc_faster_diffs):.2f}s, Min diff: {np.min(gc_faster_diffs):.2f}s, Mean diff: {np.mean(gc_faster_diffs):.2f}s, Median diff: {np.median(gc_faster_diffs):.2f}s")
print(f"Projects where pymop_no_gc is faster than pymop_gc by >0.5s: {no_gc_faster_01}")
if no_gc_faster_diffs:
    print(f"  Max diff: {np.max(no_gc_faster_diffs):.2f}s, Min diff: {np.min(no_gc_faster_diffs):.2f}s, Mean diff: {np.mean(no_gc_faster_diffs):.2f}s, Median diff: {np.median(no_gc_faster_diffs):.2f}s")
print(f"Projects where the difference is ≤0.1s (same speed): {same_speed_01}")
print()

# Write Macros for the research paper
with open('gc_comparison_macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_projects}}{{{gc_faster_01}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_projects}}{{{no_gc_faster_01}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_same_speed_0.5s_projects}}{{{same_speed_01}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_different_speed_0.5s_projects}}{{{len(filtered_projects_with_same_results) - same_speed_01}}}\n")

# ================================
# Count the number of specs used
# ================================

# Calculate the number of specs used based on the 'events' column (only for filtered and valid projects)
filtered_valid_projects = set(filtered_projects_with_same_results) & set(valid_projects)
data_filtered_valid = data[data['project'].isin(filtered_valid_projects)]

def find_multiple_events_specs(event_str):
    event_dict = {}
    specs_multiple_events = []
    if pd.isna(event_str):
        return []
    for event in event_str.split('<>'):
        if '=' in event:
            parts = event.split('=')
            spec = parts[0]
            try:
                count = int(parts[2])
            except (IndexError, ValueError):
                count = 0
            if spec in event_dict:
                event_dict[spec] += count
                specs_multiple_events.append(spec)
            else:
                event_dict[spec] = count
    return specs_multiple_events


def parse_events_str(event_str):
    event_dict = {}
    if pd.isna(event_str):
        return event_dict
    for event in event_str.split('<>'):
        if '=' in event:
            parts = event.split('=')
            spec = parts[0]
            try:
                count = int(parts[2])
            except (IndexError, ValueError):
                count = 0
            if spec in event_dict:
                event_dict[spec] += count
            else:
                event_dict[spec] = count
    return event_dict

def parse_monitors_str(monitors_str):
    monitors_dict = {}
    if pd.isna(monitors_str):
        return monitors_dict
    for monitor in monitors_str.split('<>'):
        if '=' in monitor:
            parts = monitor.split('=')
            spec = parts[0]
            try:
                count = int(parts[1])
            except (IndexError, ValueError):
                count = 0
            if spec in monitors_dict:
                monitors_dict[spec] += count
            else:
                monitors_dict[spec] = count
    return monitors_dict

def count_specs(event_dict):
    if not isinstance(event_dict, dict):
        return 0, 0
    return len(event_dict), sum(event_dict.values())

# Calculate average number of specs used per project where gc is faster and where no gc is faster (by >0.1s)
gc_faster_events_dicts = data_filtered_valid[data_filtered_valid['project'].isin(projects_gc_faster_01)]['events'].apply(parse_events_str)
no_gc_faster_events_dicts = data_filtered_valid[data_filtered_valid['project'].isin(projects_no_gc_faster_01)]['events'].apply(parse_events_str)

# Calculate average number of monitors used per project where gc is faster and where no gc is faster (by >0.1s)
gc_faster_monitors_dicts = data_filtered_valid[data_filtered_valid['project'].isin(projects_gc_faster_01)]['monitors'].apply(parse_monitors_str)
no_gc_faster_monitors_dicts = data_filtered_valid[data_filtered_valid['project'].isin(projects_no_gc_faster_01)]['monitors'].apply(parse_monitors_str)

# Get the specs that have multiple events in the test run
gc_faster_specs_multiple_events = data_filtered_valid[data_filtered_valid['project'].isin(projects_gc_faster_01)]['events'].apply(find_multiple_events_specs)
no_gc_faster_specs_multiple_events = data_filtered_valid[data_filtered_valid['project'].isin(projects_no_gc_faster_01)]['events'].apply(find_multiple_events_specs)

gc_faster_events_counts = gc_faster_events_dicts.apply(count_specs)
no_gc_faster_events_counts = no_gc_faster_events_dicts.apply(count_specs)

gc_faster_monitors_counts = gc_faster_monitors_dicts.apply(count_specs)
no_gc_faster_monitors_counts = no_gc_faster_monitors_dicts.apply(count_specs)

if not gc_faster_events_counts.empty:
    sum_gc_faster_specs = np.mean([x[0] for x in gc_faster_events_counts])
    sum_gc_faster_events_count = np.mean([x[1] for x in gc_faster_events_counts])
    sum_gc_faster_monitors_count = np.mean([x[1] for x in gc_faster_monitors_counts])
else:
    sum_gc_faster_specs = 0
    sum_gc_faster_events_count = 0
    sum_gc_faster_monitors_count = 0

if not no_gc_faster_events_counts.empty:
    sum_no_gc_faster_specs = np.mean([x[0] for x in no_gc_faster_events_counts])
    sum_no_gc_faster_events_count = np.mean([x[1] for x in no_gc_faster_events_counts])
    sum_no_gc_faster_monitors_count = np.mean([x[1] for x in no_gc_faster_monitors_counts])
else:
    sum_no_gc_faster_specs = 0
    sum_no_gc_faster_events_count = 0
    sum_no_gc_faster_monitors_count = 0

print(f"\n[Specs and events used for all projects and all specs]")
print(f"Average number of specs used per project where pymop_gc is faster (>0.5s): {sum_gc_faster_specs}")
print(f"Average number of specs used per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_specs}")
print(f"Average number of events per project where pymop_gc is faster (>0.5s): {sum_gc_faster_events_count}")
print(f"Average number of events per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_events_count}")
print(f"Average number of monitors used per project where pymop_gc is faster (>0.5s): {sum_gc_faster_monitors_count}")
print(f"Average number of monitors used per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_monitors_count}")
print()

# Write Macros for the research paper
with open('gc_comparison_macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_specs_mean}}{{{sum_gc_faster_specs:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_specs_mean}}{{{sum_no_gc_faster_specs:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_events_count_mean}}{{{sum_gc_faster_events_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_events_count_mean}}{{{sum_no_gc_faster_events_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_monitors_count_mean}}{{{sum_gc_faster_monitors_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_monitors_count_mean}}{{{sum_no_gc_faster_monitors_count:.2f}}}\n")

# List of target specs
spec_names = [
    "faulthandler_disableBeforeClose",
    "faulthandler_tracetrackDumpBeforeClose",
    "faulthandler_unregisterBeforeClose",
    "File_MustClose",
    "Flask_NoModifyAfterServe",
    "Flask_NoOptionsChangeAfterEnvCreate",
    "Flask_UnsafeFilePath",
    "Pydocs_MustCloseSocket",
    "Pydocs_MustFlushMmap",
    "PyDocs_MustOnlyUseDictReader",
    "Pydocs_MustReleaseLock",
    "Pydocs_MustReleaseRLock",
    "Pydocs_MustShutdownProcessPoolExecutor",
    "Pydocs_MustShutdownThreadPoolExecutor",
    "PyDocs_MustSortBeforeGroupBy",
    "Pydocs_MustUnlinkSharedMemory",
    "PyDocs_MustWaitForPopenToFinish",
    "Pydocs_NoReadAfterAccess",
    "Pydocs_ShouldUseStreamWriterCorrectly",
    "PyDocs_UnsafeIterUseAfterTee",
    "Pydocs_UselessFileOpen",
    "Pydocs_UselessProcessPoolExecutor",
    "Pydocs_UselessThreadPoolExecutor",
    "Requests_MustCloseSession",
    "UnsafeArrayIterator",
    "UnsafeListIterator",
    "UnsafeMapIterator",
    "XMLParser_ParseMustFinalize",
]

def count_multiple_objects_specs(event_dict):
    if not isinstance(event_dict, dict):
        return 0, 0
    else:
        spec_count = 0
        events_count = 0
        for spec, event_count in event_dict.items():
            if spec in spec_names:
                spec_count += 1
                events_count += event_count
        return spec_count, events_count

gc_faster_counts_mutiple_objects = gc_faster_events_dicts.apply(count_multiple_objects_specs)
no_gc_faster_counts_mutiple_objects = no_gc_faster_events_dicts.apply(count_multiple_objects_specs)

gc_faster_monitors_counts_mutiple_objects = gc_faster_monitors_dicts.apply(count_multiple_objects_specs)
no_gc_faster_monitors_counts_mutiple_objects = no_gc_faster_monitors_dicts.apply(count_multiple_objects_specs)

if not gc_faster_counts_mutiple_objects.empty:
    sum_gc_faster_multiple_objects_specs = np.mean([x[0] for x in gc_faster_counts_mutiple_objects])
    sum_gc_faster_multiple_objects_events_count = np.mean([x[1] for x in gc_faster_counts_mutiple_objects])
    sum_gc_faster_multiple_objects_monitors_count = np.mean([x[1] for x in gc_faster_monitors_counts_mutiple_objects])
else:
    sum_gc_faster_multiple_objects_specs = 0
    sum_gc_faster_multiple_objects_events_count = 0
    sum_gc_faster_multiple_objects_monitors_count = 0

if not no_gc_faster_counts_mutiple_objects.empty:
    sum_no_gc_faster_multiple_objects_specs = np.mean([x[0] for x in no_gc_faster_counts_mutiple_objects])
    sum_no_gc_faster_multiple_objects_events_count = np.mean([x[1] for x in no_gc_faster_counts_mutiple_objects])
    sum_no_gc_faster_multiple_objects_monitors_count = np.mean([x[1] for x in no_gc_faster_monitors_counts_mutiple_objects])
else:
    sum_no_gc_faster_multiple_objects_specs = 0
    sum_no_gc_faster_multiple_objects_events_count = 0
    sum_no_gc_faster_multiple_objects_monitors_count = 0

print(f"\n[Specs and events used for all projects and multiple objects specs]")
print(f"Average number of multiple objects specs used per project where pymop_gc is faster (>0.5s): {sum_gc_faster_multiple_objects_specs}")
print(f"Average number of multiple objects specs used per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_multiple_objects_specs}")
print(f"Average number of multiple objects events per project where pymop_gc is faster (>0.5s): {sum_gc_faster_multiple_objects_events_count}")
print(f"Average number of multiple objects events per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_multiple_objects_events_count}")
print(f"Average number of multiple objects monitors used per project where pymop_gc is faster (>0.5s): {sum_gc_faster_multiple_objects_monitors_count}")
print(f"Average number of multiple objects monitors used per project where pymop_no_gc is faster (>0.5s): {sum_no_gc_faster_multiple_objects_monitors_count}")
print()

# Write Macros for the research paper
with open('gc_comparison_macros.tex', 'a') as f:
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_multiple_objects_specs_mean}}{{{sum_gc_faster_multiple_objects_specs:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_multiple_objects_specs_mean}}{{{sum_no_gc_faster_multiple_objects_specs:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_multiple_objects_events_count_mean}}{{{sum_gc_faster_multiple_objects_events_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_multiple_objects_events_count_mean}}{{{sum_no_gc_faster_multiple_objects_events_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_gc_faster_0.5s_multiple_objects_monitors_count_mean}}{{{sum_gc_faster_multiple_objects_monitors_count:.2f}}}\n")
    f.write(f"\\DefMacro{{gc_comparison_macros_no_gc_faster_0.5s_multiple_objects_monitors_count_mean}}{{{sum_no_gc_faster_multiple_objects_monitors_count:.2f}}}\n")
