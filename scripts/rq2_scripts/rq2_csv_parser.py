# Import necessary libraries
import os
import json
import subprocess
from collections import OrderedDict
from collections import Counter
import re
import csv

def get_time_from_json(projectname, algorithm):
    """Extract time information from JSON file"""
    filename = f'{algorithm}-time.json'
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        json_data = json.load(f)

    instrumentation_duration = json_data.get('instrumentation_duration', 0)
    create_monitor_duration = json_data.get('create_monitor_duration', 0)
    test_duration = json_data.get('test_duration', 0)

    return instrumentation_duration, create_monitor_duration, test_duration

def get_monitors_and_events_from_json(projectname, algorithm):
    """Extract monitor and event information from JSON file"""
    filename = f'{algorithm}-full.json'
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        json_data = json.load(f)

    return_str_monitors = ""
    return_str_events = ""
    total_monitors = 0
    total_events = 0

    for spec in json_data.keys():
        num_monitors = json_data[spec]["monitors"]
        total_events_spec = sum(json_data[spec]["events"].values())
        return_str_monitors += f'{spec}={num_monitors}<>'
        for event, count in json_data[spec]["events"].items():
            return_str_events += f'{spec}={event}={count}<>'
        total_monitors += num_monitors
        total_events += total_events_spec

    return return_str_monitors[:-2], return_str_events[:-2], total_monitors, total_events

def get_num_violations_from_json(projectname, algorithm):
    """Extract violation information from JSON file"""
    filename = f'{algorithm}-violations.json'
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        json_data = json.load(f)

    return_spec_string = ""
    total_violations = 0
    unique_violations_count = ""
    unique_violations_summary = {}
    unique_violations_test = {}
    violations_by_location = {}  # New dict to track violations by file and line

    for spec in json_data.keys():
        size = len(json_data[spec])
        return_spec_string += f'{spec}={size};'

        violations = []
        violations_test = {}
        for item in json_data[spec]:
            violations.append(item['violation'])
            if violations_test.get(item['violation']) is None:
                violations_test[item['violation']] = set()
            violations_test[item['violation']].add(item['test'])
            
            # Extract file name and line number from violation string
            violation_str = item['violation']
            if 'file_name:' in violation_str and 'line_num:' in violation_str:
                file_name = violation_str.split('file_name:')[1].split(',')[0].strip()
                line_num = violation_str.split('line_num:')[1].strip()
                location_key = f"{file_name}:{line_num}"
                violations_by_location[location_key] = violations_by_location.get(location_key, 0) + 1

        violations_counter = Counter(violations)

        unique_violations_summary[spec] = dict(violations_counter)
        unique_violations_test[spec] = dict(violations_test)
        unique_violations_count += f'{spec}={len(dict(violations_counter))};'

        total_violations += size

    return (return_spec_string[:-1], total_violations, unique_violations_count, unique_violations_summary,
            unique_violations_test, violations_by_location)

def clean_tool_path(filepath, project, tool):
    """Clean up file paths by removing workspace and project prefix for all tools"""
    if tool == "pymop":
        prefix = f"/workspace/{project}_PyMOP/"
    elif tool == "dynapyt":
        prefix = f"/workspace/{project}_DynaPyt/"
    elif tool == "dynapyt_libs":
        prefix = f"/workspace/{project}_DynaPyt_Libs/"
    else:
        return filepath
        
    if filepath.startswith(prefix):
        cleaned_path = filepath[len(prefix):]
        # Remove .orig suffix for Dynapyt and Dynapyt with library cases
        if tool in ["dynapyt", "dynapyt_libs"] and cleaned_path.endswith(".orig"):
            cleaned_path = cleaned_path[:-5]  # Remove .orig suffix
        return f"{project}/{cleaned_path}"
    return filepath

def results_csv_file(lines):
    """Write results to a CSV file"""
    if not lines:
        print('No data to write.')
        return

    max_columns_line = max(lines, key=lambda line: len(line.keys()))

    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=max_columns_line.keys())
        writer.writeheader()
        for line in lines:
            if 'execution_problems' in line:
                del line['execution_problems']
            # Convert violations_by_location dict to string if it exists and is a dict
            if isinstance(line.get('violations_by_location'), dict):
                # Clean up file paths based on the tool type
                cleaned_violations = {}
                for loc, count in line['violations_by_location'].items():
                    filepath, line_num = loc.rsplit(':', 1)
                    cleaned_path = clean_tool_path(filepath, line['project'], line['type_project'].lower())
                    clean_loc = f"{cleaned_path}:{line_num}"
                    cleaned_violations[clean_loc] = count
                line['violations_by_location'] = ';'.join(f"{loc}={count}" for loc, count in cleaned_violations.items())
            try:
                writer.writerow(line)
            except Exception as e:
                print('could not write line:', line.keys(), str(e))

    print('CSV file created successfully.')

def process_test_summary(test_summary):
    """Process test summary to extract time and test results"""
    time = None
    if test_summary:
        parts = test_summary.split()
        for part in parts:
            if part.endswith('s') and parts[parts.index(part)-1] == "in":
                time = part[:-1]
    return time

def create_base_data_structure(project, algorithm):
    """Create base OrderedDict for test results"""
    return OrderedDict({
        'project': project,
        'algorithm': algorithm,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'xfailed': 0,
        'xpassed': 0,
        'errors': 0,
        'time': None,
        'type_project': algorithm,
        'time_instrumentation': 'x',
        'time_create_monitor': 'x',
        'test_duration': 'x',
        'post_run_time': 'x',           # New field for Post-Run Time
        'end_to_end_time': 'x',
        'total_violations': 'x',
        'violations': '',
        'unique_violations_count': '',
        'violations_by_location': '',  # New field for violations by location
    })

def process_test_results(test_summary, time, line):
    """Process test results and update line dictionary"""
    if test_summary and time:
        parts = test_summary.split()
        for i in range(len(parts)):
            for key in line.keys():
                if key in parts[i].lower():
                    try:
                        line[key] = int(parts[i-1])
                    except ValueError:
                        pass
    else:
        columns_to_cross_out = ['passed', 'failed', 'skipped', 'xfailed', 'xpassed', 'errors', 'time']
        for column in columns_to_cross_out:
            line[column] = 'x'

def get_test_info_from_files(result_file, output_file):
    """Extract test information from result and output files"""
    test_duration = "x"
    end_to_end_time = "x"
    post_run_time = "x"
    if result_file is not None:
        with open(result_file, 'r') as file:
            for l in file:
                if 'Test Time:' in l:
                    test_time = l.split(' ')[-1].replace('s', '').strip()
                    if test_time != "Timeout":
                        test_duration = float(test_time)
                        end_to_end_time = float(test_time)
                elif 'Post-Run Time:' in l:
                    post_run_time_val = l.split('Post-Run Time:')[1].strip()
                    if post_run_time_val.endswith('s'):
                        post_run_time_val = post_run_time_val[:-1]
                    try:
                        post_run_time = float(post_run_time_val)
                    except ValueError:
                        post_run_time = post_run_time_val

    test_summary = None
    if output_file:
        with open(output_file, 'r') as file:
            for line in reversed(file.readlines()):
                if "in" in line:
                    for part in ['passed', 'failed', 'skipped', 'xfailed', 'xpassed', 'errors']:
                        if part in line.lower():
                            test_summary = line.strip()
                            break
                
                if test_summary:
                    break

    return test_duration, end_to_end_time, test_summary, post_run_time

def main():
    """Main function to process projects and generate results"""
    lines = []

    # Get all project names
    projects = set()
    for folder in sorted(os.listdir('.')):
        if os.path.isdir(folder):
            if folder.endswith('_Original'):
                project_name = folder.rsplit('_', 1)[0]
                projects.add(project_name)

    # Build the folder name for each project (original, pymop, dynapyt runs)
    for project in sorted(projects):
        original_folder = f"{project}_Original/{project}_Original"
        pymop_monkey_folder = f"{project}_Pymop_monkey/{project}_Pymop_monkey"
        pymop_curses_folder = f"{project}_Pymop_curses/{project}_Pymop_curses"
        pymop_ast_folder = f"{project}_Pymop_ast/{project}_Pymop_ast"


        # ===============================================
        # Process Original files
        # ===============================================

        # Change to the original folder
        os.chdir(original_folder)

        # Get all files in the original folder
        files = os.listdir()

        # Get the result and output files
        result_files = [f for f in files if f.endswith(f'results.txt')]
        output_files = [f for f in files if f.endswith('Output.txt')]

        # If no result or output files, print error and skip to next project
        if not result_files or not output_files:
            print(f'No original files found for {project}')
            result_file = None
            output_file = None
        else:
            # Get the first result and output files
            result_file = result_files[0]
            output_file = output_files[0]

        # Get the test duration, end-to-end time, and test summary
        algorithm = 'original'
        test_duration, end_to_end_time, test_summary, post_run_time = get_test_info_from_files(result_file, output_file)

        # If no result file, print error and skip to next project
        if result_file is None:
            print(f"No test results found for {project} with algorithm {algorithm}")
            os.chdir('../..')
            continue

        # Get the time from the test summary
        time = process_test_summary(test_summary)

        # If no test summary, print error and skip to next project
        if not test_summary:
            print(f"No test summary found for {project} with algorithm {algorithm}")
            os.chdir('../..')
            continue

        # Create the base data structure
        line = create_base_data_structure(project, algorithm)

        # Process the test results
        line['time'] = time
        process_test_results(test_summary, time, line)

        # Add the type of project
        line['type_project'] = 'original'

        # Add the instrumentation time
        line['time_instrumentation'] = 0.0

        # Add the test duration
        line['test_duration'] = test_duration

        # Add the time to create the monitor
        line['time_create_monitor'] = 0.0

        # Add end-to-end time
        line['end_to_end_time'] = end_to_end_time

        # Add the post-run time
        line['post_run_time'] = 0.0

        # Add the line to the lines list
        lines.append(line)

        # Change to the original folder
        os.chdir('../..')

        # ===============================================
        # Process Pymop files with monkey_patching
        # ===============================================

        # If no pymop folder, print error and skip to next project
        if not os.path.exists(pymop_monkey_folder):
            print(f'No pymop with monkey patching folder found for {project}')
            line = OrderedDict({
                'project': project,
                'algorithm': 'D',
                'passed': 'x',
                'failed': 'x',
                'skipped': 'x',
                'xfailed': 'x',
                'xpassed': 'x',
                'errors': 'x',
                'time': 'x',
                'type_project': 'monkey patching',
                'time_instrumentation': 'x',
                'test_duration': 'x',
                'time_create_monitor': 'x',
                'total_violations': 'x',
                'violations': 'x',
                'unique_violations_count': 'x',
                'monitors': 'x',
                'total_monitors': 'x',
                'events': 'x',
                'total_events': 'x',
                'end_to_end_time': 'x',
                'post_run_time': 'x',
            })
            lines.append(line)
        else:
            os.chdir(pymop_monkey_folder)

            # Process Algorithm D results
            for algorithm in ["D"]:
                files = os.listdir()
                result_files = [f for f in files if f.endswith(f'results.txt')]
                output_files = [f for f in files if f.endswith('_Output.txt')]

                # If no result or output files, print error and skip to next project
                if not result_files or not output_files:
                    print(f'No pymop with monkey patching files found for {project}')
                    result_file = None
                    output_file = None
                else:
                    result_file = result_files[0]
                    output_file = output_files[0]

                # Get the test duration, end-to-end time, and test summary
                test_duration, end_to_end_time, test_summary, post_run_time = get_test_info_from_files(result_file, output_file)

                # Get the time from the test summary
                time = process_test_summary(test_summary)

                # Create the base data structure
                line = create_base_data_structure(project, algorithm)
                line['time'] = time
                process_test_results(test_summary, time, line)

                # Set the type of project
                line['type_project'] = 'monkey patching'

                # Get the instrumentation time, create monitor time, and test duration
                try:
                    ret_time = get_time_from_json(project, algorithm)
                except Exception as e:
                    ret_time = None

                # If ret_time is not None, set the instrumentation time, create monitor time, and test duration
                if ret_time is not None and time is not None and isinstance(end_to_end_time, float) and isinstance(test_duration, float):
                    (instrumentation_duration, create_monitor_duration, _) = ret_time
                    line['time_instrumentation'] = instrumentation_duration
                    line['time_create_monitor'] = create_monitor_duration
                    line['test_duration'] = end_to_end_time - instrumentation_duration - create_monitor_duration
                    line['end_to_end_time'] = end_to_end_time
                else:
                    line['time_instrumentation'] = 'x'
                    line['time_create_monitor'] = 'x'
                    line['test_duration'] = 'x'
                    line['end_to_end_time'] = 'x'

                if algorithm != "ORIGINAL":
                    ret_violation = get_num_violations_from_json(project, algorithm)

                    if ret_violation is not None:
                        (
                            violations_str,
                            total_violations,
                            unique_violations_count,
                            unique_violations_summary,
                            unique_violations_test,
                            violations_by_location
                        ) = (
                            ret_violation[0],
                            ret_violation[1],
                            ret_violation[2],
                            ret_violation[3],
                            ret_violation[4],
                            ret_violation[5]
                        )
                    
                        line['total_violations'] = total_violations
                        line['violations'] = violations_str
                        line['unique_violations_count'] = unique_violations_count
                        str_unique_violations_summary = str(unique_violations_summary).replace(",", "<>")
                        line['unique_violations_summary'] = str_unique_violations_summary
                        str_unique_violations_test = str(unique_violations_test).replace(",", "<>")
                        line['unique_violations_test'] = str_unique_violations_test
                        line['violations_by_location'] = violations_by_location  # Add the violations by location

                        del line['unique_violations_summary']
                        del line['unique_violations_test']

                    ret_full = get_monitors_and_events_from_json(project, algorithm)

                    if ret_full is not None:
                        monitors_str, events_str, total_monitors, total_events = ret_full[0], ret_full[1], ret_full[2], ret_full[3]

                        line['monitors'] = monitors_str
                        line['total_monitors'] = total_monitors
                        line['events'] = events_str
                        line['total_events'] = total_events

                    # Add the post-run time
                    line['post_run_time'] = 0.0

                lines.append(line)

            # Change to the pymop folder
            os.chdir('../..')

        # ===============================================
        # Process Pymop files with curses
        # ===============================================

        # If no pymop folder, print error and skip to next project
        if not os.path.exists(pymop_curses_folder):
            print(f'No pymop with curses folder found for {project}')
            line = OrderedDict({
                'project': project,
                'algorithm': 'D',
                'passed': 'x',
                'failed': 'x',
                'skipped': 'x',
                'xfailed': 'x',
                'xpassed': 'x',
                'errors': 'x',
                'time': 'x',
                'type_project': 'monkey patching',
                'time_instrumentation': 'x',
                'test_duration': 'x',
                'time_create_monitor': 'x',
                'total_violations': 'x',
                'violations': 'x',
                'unique_violations_count': 'x',
                'monitors': 'x',
                'total_monitors': 'x',
                'events': 'x',
                'total_events': 'x',
                'end_to_end_time': 'x',
                'post_run_time': 'x',
            })
            lines.append(line)
        else:
            os.chdir(pymop_curses_folder)

            # Process Algorithm D results
            for algorithm in ["D"]:
                files = os.listdir()
                result_files = [f for f in files if f.endswith(f'results.txt')]
                output_files = [f for f in files if f.endswith('_Output.txt')]

                # If no result or output files, print error and skip to next project
                if not result_files or not output_files:
                    print(f'No pymop with curses files found for {project}')
                    result_file = None
                    output_file = None
                else:
                    result_file = result_files[0]
                    output_file = output_files[0]

                # Get the test duration, end-to-end time, and test summary
                test_duration, end_to_end_time, test_summary, post_run_time = get_test_info_from_files(result_file, output_file)

                # Get the time from the test summary
                time = process_test_summary(test_summary)

                # Create the base data structure
                line = create_base_data_structure(project, algorithm)
                line['time'] = time
                process_test_results(test_summary, time, line)

                # Set the type of project
                line['type_project'] = 'curse'

                # Get the instrumentation time, create monitor time, and test duration
                try:
                    ret_time = get_time_from_json(project, algorithm)
                except Exception as e:
                    ret_time = None

                # If ret_time is not None, set the instrumentation time, create monitor time, and test duration
                if ret_time is not None and time is not None and isinstance(end_to_end_time, float) and isinstance(test_duration, float):
                    (instrumentation_duration, create_monitor_duration, _) = ret_time
                    line['time_instrumentation'] = instrumentation_duration
                    line['time_create_monitor'] = create_monitor_duration
                    line['test_duration'] = end_to_end_time - instrumentation_duration - create_monitor_duration
                    line['end_to_end_time'] = end_to_end_time
                else:
                    line['time_instrumentation'] = 'x'
                    line['time_create_monitor'] = 'x'
                    line['test_duration'] = 'x'
                    line['end_to_end_time'] = 'x'

                if algorithm != "ORIGINAL":
                    ret_violation = get_num_violations_from_json(project, algorithm)

                    if ret_violation is not None:
                        (
                            violations_str,
                            total_violations,
                            unique_violations_count,
                            unique_violations_summary,
                            unique_violations_test,
                            violations_by_location
                        ) = (
                            ret_violation[0],
                            ret_violation[1],
                            ret_violation[2],
                            ret_violation[3],
                            ret_violation[4],
                            ret_violation[5]
                        )
                    
                        line['total_violations'] = total_violations
                        line['violations'] = violations_str
                        line['unique_violations_count'] = unique_violations_count
                        str_unique_violations_summary = str(unique_violations_summary).replace(",", "<>")
                        line['unique_violations_summary'] = str_unique_violations_summary
                        str_unique_violations_test = str(unique_violations_test).replace(",", "<>")
                        line['unique_violations_test'] = str_unique_violations_test
                        line['violations_by_location'] = violations_by_location  # Add the violations by location

                        del line['unique_violations_summary']
                        del line['unique_violations_test']

                    ret_full = get_monitors_and_events_from_json(project, algorithm)

                    if ret_full is not None:
                        monitors_str, events_str, total_monitors, total_events = ret_full[0], ret_full[1], ret_full[2], ret_full[3]

                        line['monitors'] = monitors_str
                        line['total_monitors'] = total_monitors
                        line['events'] = events_str
                        line['total_events'] = total_events

                    # Add the post-run time
                    line['post_run_time'] = 0.0

                lines.append(line)

            # Change to the pymop folder
            os.chdir('../..')
    
        # ===============================================
        # Process Pymop files with ast
        # ===============================================

        # If no pymop folder, print error and skip to next project
        if not os.path.exists(pymop_ast_folder):
            print(f'No pymop with ast folder found for {project}')
            line = OrderedDict({
                'project': project,
                'algorithm': 'D',
                'passed': 'x',
                'failed': 'x',
                'skipped': 'x',
                'xfailed': 'x',
                'xpassed': 'x',
                'errors': 'x',
                'time': 'x',
                'type_project': 'monkey patching',
                'time_instrumentation': 'x',
                'test_duration': 'x',
                'time_create_monitor': 'x',
                'total_violations': 'x',
                'violations': 'x',
                'unique_violations_count': 'x',
                'monitors': 'x',
                'total_monitors': 'x',
                'events': 'x',
                'total_events': 'x',
                'end_to_end_time': 'x',
            })
            lines.append(line)
        else:
            os.chdir(pymop_ast_folder)

            # Process Algorithm D results
            for algorithm in ["D"]:
                files = os.listdir()
                result_files = [f for f in files if f.endswith(f'results.txt')]
                output_files = [f for f in files if f.endswith('_Output.txt')]

                # If no result or output files, print error and skip to next project
                if not result_files or not output_files:
                    print(f'No pymop with ast files found for {project}')
                    result_file = None
                    output_file = None
                else:
                    result_file = result_files[0]
                    output_file = output_files[0]

                # Get the test duration, end-to-end time, and test summary
                test_duration, end_to_end_time, test_summary, post_run_time = get_test_info_from_files(result_file, output_file)

                # Get the time from the test summary
                time = process_test_summary(test_summary)

                # Create the base data structure
                line = create_base_data_structure(project, algorithm)
                line['time'] = time
                process_test_results(test_summary, time, line)

                # Set the type of project
                line['type_project'] = 'ast'

                # Get the instrumentation time, create monitor time, and test duration
                try:
                    ret_time = get_time_from_json(project, algorithm)
                except Exception as e:
                    ret_time = None

                # If ret_time is not None, set the instrumentation time, create monitor time, and test duration
                if ret_time is not None and time is not None and isinstance(end_to_end_time, float) and isinstance(test_duration, float):
                    (instrumentation_duration, create_monitor_duration, _) = ret_time
                    line['time_instrumentation'] = instrumentation_duration
                    line['time_create_monitor'] = create_monitor_duration
                    line['test_duration'] = end_to_end_time - instrumentation_duration - create_monitor_duration
                    line['end_to_end_time'] = end_to_end_time
                else:
                    line['time_instrumentation'] = 'x'
                    line['time_create_monitor'] = 'x'
                    line['test_duration'] = 'x'
                    line['end_to_end_time'] = 'x'

                if algorithm != "ORIGINAL":
                    ret_violation = get_num_violations_from_json(project, algorithm)

                    if ret_violation is not None:
                        (
                            violations_str,
                            total_violations,
                            unique_violations_count,
                            unique_violations_summary,
                            unique_violations_test,
                            violations_by_location
                        ) = (
                            ret_violation[0],
                            ret_violation[1],
                            ret_violation[2],
                            ret_violation[3],
                            ret_violation[4],
                            ret_violation[5]
                        )
                    
                        line['total_violations'] = total_violations
                        line['violations'] = violations_str
                        line['unique_violations_count'] = unique_violations_count
                        str_unique_violations_summary = str(unique_violations_summary).replace(",", "<>")
                        line['unique_violations_summary'] = str_unique_violations_summary
                        str_unique_violations_test = str(unique_violations_test).replace(",", "<>")
                        line['unique_violations_test'] = str_unique_violations_test
                        line['violations_by_location'] = violations_by_location  # Add the violations by location

                        del line['unique_violations_summary']
                        del line['unique_violations_test']

                    ret_full = get_monitors_and_events_from_json(project, algorithm)

                    if ret_full is not None:
                        monitors_str, events_str, total_monitors, total_events = ret_full[0], ret_full[1], ret_full[2], ret_full[3]

                        line['monitors'] = monitors_str
                        line['total_monitors'] = total_monitors
                        line['events'] = events_str
                        line['total_events'] = total_events

                    # Add the post-run time
                    line['post_run_time'] = 0.0

                lines.append(line)

            # Change to the pymop folder
            os.chdir('../..')

    # Print the results
    print("\n====== RESULTS CSV ======\n")
    results_csv_file(lines)
    print('created results.csv')

main()
