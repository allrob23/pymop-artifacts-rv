import csv
from collections import defaultdict

# Input and output file paths
input_csv = 'algos_comparison_consistent_results.csv'
output_csv = 'algos_comparison_consistent_time_results.csv'

# The algorithms to extract, in order
algos = ['ORIGINAL', 'B', 'C', 'C+', 'D']
output_headers = ['project', 'original', 'b', 'c', 'c+', 'd']

# Collect test_duration for each project and algorithm
project_data = defaultdict(dict)

# Read the input CSV file
with open(input_csv, newline='') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        project = row['project']
        algo = row['algorithm']
        if algo in algos:
            test_duration = row.get('test_duration', '').strip()
            try:
                test_duration = str(round(float(test_duration), 2))
            except (ValueError, TypeError):
                test_duration = ''
            project_data[project][algo] = test_duration

# Write the output CSV
with open(output_csv, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(output_headers)
    for project in sorted(project_data.keys()):
        row = [project]
        for algo in algos:
            row.append(project_data[project].get(algo, ''))
        writer.writerow(row)
