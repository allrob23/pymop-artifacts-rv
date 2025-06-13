import os
import sys
import argparse
import csv
import statistics

def load(args):
    loaded = {}
    with open(args.overheadalgo, mode = 'r') as overhead_file:
        reader = csv.DictReader(overhead_file)
        for row in reader:
            project = row['project']
            if project == 'lobziik-pytest_samples':
                continue
            loaded[project] = {
                'original': float(row['original']),
                'b': float(row['b']),
                'c': float(row['c']),
                'c+': float(row['c+']),
                'd': float(row['d'])
            }
        return loaded


def summarize_list(lst, label, overhead):
    summary = {}
    summary['total-' + label + '-' + overhead] = sum(lst)
    summary['mean-' + label + '-' + overhead] = statistics.mean(lst)
    summary['max-' + label + '-' + overhead] = max(lst)
    summary['min-' + label + '-' + overhead] = min(lst)
    summary['median-' + label + '-' + overhead] = statistics.median(lst)
    print(label + ' ' + overhead + ' is {}'.format(statistics.mean(lst)) )
    return summary


def summarize_all(data, percentiles, label):
    summary = {}

    lst = [data[key]['b'] / data[key]['original'] for key in data.keys() if key in percentiles]
    summary = {**summary, **summarize_list(lst, label, 'b-rel')}
    
    lst = [data[key]['c'] / data[key]['original'] for key in data.keys() if key in percentiles]
    summary = {**summary, **summarize_list(lst, label, 'c-rel')}
    
    lst = [data[key]['c+'] / data[key]['original'] for key in data.keys() if key in percentiles]
    summary = {**summary, **summarize_list(lst, label, 'cplus-rel')}
    
    lst = [data[key]['d'] / data[key]['original'] for key in data.keys() if key in percentiles]
    summary = {**summary, **summarize_list(lst, label, 'd-rel')}
    
    return summary


def count_fastest_algos(data, percentiles):
    fastest_counts = {}
    fatest_projects = {}
    for label, projects in percentiles.items():
        counts = {'b': 0, 'c': 0, 'c+': 0, 'd': 0}
        fastest_projects_decile = {'b': [], 'c': [], 'c+': [], 'd': []}
        for project in projects:
            algos = {algo: data[project][algo] for algo in ['b', 'c', 'c+', 'd']}
            fastest = min(algos, key=algos.get)
            counts[fastest] += 1
            fastest_projects_decile[fastest].append(project)
        fastest_counts[label] = counts
        fatest_projects[label] = fastest_projects_decile
    return fastest_counts, fatest_projects


def count_fastest_algos_with_threshold(data, percentiles, threshold):
    fastest_counts = {}
    for label, projects in percentiles.items():
        counts = {'b': 0, 'c': 0, 'c+': 0, 'd': 0, 'all': 0}
        for project in projects:
            algos = {algo: data[project][algo] for algo in ['b', 'c', 'd']}
            mean_duration = sum(algos.values()) / len(algos)
            threshold_duration = mean_duration - threshold
            fastest_algo = None
            fastest_duration = 0.0
            for algo, duration in algos.items():
                if duration < threshold_duration:
                    if fastest_algo is None or duration < fastest_duration:
                        fastest_algo = algo
                        fastest_duration = duration
            if fastest_algo is None:
                counts['all'] += 1
            else:
                counts[fastest_algo] += 1
        fastest_counts[label] = counts
    return fastest_counts


def summarize_per_percentile(args, data):
    percentiles = {'p' + str(i) : [] for i in range(1, 11)}
    projects_count = len(data)
    counter = 0
    
    for project in sorted(data.items(), key=lambda item: item[1]['d'] - item[1]['original']):
        counter += 1
        for p in range(1, 11):
            if counter <= round((p * projects_count) / 10):
                percentiles['p' + str(p)].append(project[0])
                break

    summaries = {}
    for key in percentiles.keys():
        summaries = {**summaries, **summarize_all(data, percentiles[key], key)}

    # Count and print fastest algorithm counts per percentile
    fastest_counts, fastest_projects = count_fastest_algos(data, percentiles)
    print("\nFastest algorithm counts per percentile:")
    print("Percentile |   b   |   c   |  c+  |   d  |  total")
    print("------------------------------------------------")
    for label in percentiles.keys():
        counts = fastest_counts[label]
        print(f"{label:10} | {counts['b']:5} | {counts['c']:5} | {counts['c+']:5} | {counts['d']:5} | {sum(counts.values()):5}")

    # Count and print fastest algorithm counts per percentile with threshold of 1s
    fastest_counts_with_1s_threshold = count_fastest_algos_with_threshold(data, percentiles, 1)
    print("\nFastest algorithm counts per percentile with threshold 1s:")
    print("Percentile |   b   |   c   |  c+  |   d  | same |  total")
    print("------------------------------------------------")
    for label in percentiles.keys():
        counts = fastest_counts_with_1s_threshold[label]
        print(f"{label:10} | {counts['b']:5} | {counts['c']:5} | {counts['c+']:5} | {counts['d']:5} | {counts['all']:5} | {sum(counts.values()):5}")

    # Count and print fastest algorithm counts per percentile with threshold of 2s
    fastest_counts_with_2s_threshold = count_fastest_algos_with_threshold(data, percentiles, 2)
    print("\nFastest algorithm counts per percentile with threshold 2s:")
    print("Percentile |   b   |   c   |  c+  |   d  | same |  total")
    print("------------------------------------------------")
    for label in percentiles.keys():
        counts = fastest_counts_with_2s_threshold[label]
        print(f"{label:10} | {counts['b']:5} | {counts['c']:5} | {counts['c+']:5} | {counts['d']:5} | {counts['all']:5} | {sum(counts.values()):5}")

    # Count and print fastest algorithm counts per percentile with threshold of 5s
    fastest_counts_with_5s_threshold = count_fastest_algos_with_threshold(data, percentiles, 5)
    print("\nFastest algorithm counts per percentile with threshold 5s:")
    print("Percentile |   b   |   c   |  c+  |   d  | same |  total")
    print("------------------------------------------------")
    for label in percentiles.keys():
        counts = fastest_counts_with_5s_threshold[label]
        print(f"{label:10} | {counts['b']:5} | {counts['c']:5} | {counts['c+']:5} | {counts['d']:5} | {counts['all']:5} | {sum(counts.values()):5}")

    # Calculate cumulative fastest algorithm counts
    fastest_all_counts = {'b': 0, 'c': 0, 'c+': 0, 'd': 0}
    for fastest_count in fastest_counts.values():
        for algo in ['b', 'c', 'c+', 'd']:
            fastest_all_counts[algo] += fastest_count[algo]

    fastest_2s_all_counts = {'b': 0, 'c': 0, 'd': 0, 'all': 0}
    for fastest_count in fastest_counts_with_2s_threshold.values():
        for algo in ['b', 'c', 'd', 'all']:
            fastest_2s_all_counts[algo] += fastest_count[algo]

    fastest_5s_all_counts = {'b': 0, 'c': 0, 'd': 0, 'all': 0}
    for fastest_count in fastest_counts_with_5s_threshold.values():
        for algo in ['b', 'c', 'd', 'all']:
            fastest_5s_all_counts[algo] += fastest_count[algo]

    # Find the projects that are fastest in each algorithm
    cumulative_fastest_projects = {'b': [], 'c': [], 'c+': [], 'd': []}
    for label, projects in fastest_projects.items():
        for algo in ['b', 'c', 'c+', 'd']:
            cumulative_fastest_projects[algo] += projects[algo]

    # Find the projects that are fastest in D
    fastest_projects_algo_d = cumulative_fastest_projects['d']
    
    # Calculate differences between D and second fastest algorithm for projects that are fastest in D
    d_vs_second_fastest_diffs = []
    for project in fastest_projects_algo_d:
        # Get all algorithm times for this project
        algo_times = {algo: data[project][algo] for algo in ['b', 'c', 'c+', 'd']}
        # Remove D's time to find second fastest
        algo_times.pop('d')
        second_fastest_time = min(algo_times.values())
        d_time = data[project]['d']
        d_vs_second_fastest_diffs.append(second_fastest_time - d_time)
    
    # Calculate statistics for the differences between D and second fastest algorithm for projects that are fastest in D
    mean_diff = statistics.mean(d_vs_second_fastest_diffs)
    median_diff = statistics.median(d_vs_second_fastest_diffs)
    
    # Print statistics for the differences between D and second fastest algorithm for projects that are fastest in D
    print(f"\nFor projects where D was fastest:")
    print(f"Mean difference between D and second fastest: {mean_diff:.2f} seconds")
    print(f"Median difference between D and second fastest: {median_diff:.2f} seconds")
    mean_macro = f"\\DefMacro{{fastest-D-vs-second-fastest-diff-mean}}{{{mean_diff:.2f}}}"
    median_macro = f"\\DefMacro{{fastest-D-vs-second-fastest-diff-median}}{{{median_diff:.2f}}}"

    # Save last decile (p10) project results to a new CSV file
    last_decile_label = 'p10'
    last_decile_projects = percentiles[last_decile_label]
    output_csv = 'last_decile_projects.csv'
    if last_decile_projects:
        # Get the fieldnames from the first project
        first_project = last_decile_projects[0]
        fieldnames = ['project', 'original', 'b', 'c', 'c+', 'd']
        with open(output_csv, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for project in last_decile_projects:
                row = {'project': project}
                row.update({algo: data[project][algo] for algo in ['original', 'b', 'c', 'c+', 'd']})
                writer.writerow(row)

    # Make macros for all the results
    return make_overhead_macros(summaries) + make_fastest_macros(fastest_counts) + make_fastest_threshold_macros(fastest_counts_with_1s_threshold, 1) + make_fastest_threshold_macros(fastest_counts_with_2s_threshold, 2) + make_fastest_threshold_macros(fastest_counts_with_5s_threshold, 5) + make_fastest_all_macros(fastest_all_counts) + make_fastest_threshold_all_macros(fastest_2s_all_counts, 2) + make_fastest_threshold_all_macros(fastest_5s_all_counts, 5) + [mean_macro, median_macro]


def make_overhead_macros(stats):
    macros = []
    for key in stats.keys():
        macros.append('\DefMacro{overhead-' + key + '}{'+ str(round(stats[key], 2)) + '}')
    return macros


def make_fastest_macros(fastest_counts):
    fastest_macros = []
    for label, counts in fastest_counts.items():
        for algo in ['b', 'c', 'c+', 'd']:
            algoname = algo.replace('+','plus')
            macro = f"\\DefMacro{{fastest-count-{label}-{algoname}}}{{{counts[algo]}}}"
            fastest_macros.append(macro)
    return fastest_macros


def make_fastest_threshold_macros(fastest_counts, threshold):
    fastest_macros = []
    for label, counts in fastest_counts.items():
        for algo in ['b', 'c', 'c+', 'd', 'all']:
            algoname = algo.replace('+','plus')
            macro = f"\\DefMacro{{fastest-count-{threshold}s-{label}-{algoname}}}{{{counts[algo]}}}"
            fastest_macros.append(macro)
    return fastest_macros


def make_fastest_all_macros(fastest_all_counts):
    fastest_all_macros = []
    projects_count = sum(fastest_all_counts.values())
    for algo in ['b', 'c', 'c+', 'd']:
        algoname = algo.replace('+','plus')
        macro = f"\\DefMacro{{fastest-all-count-{algoname}}}{{{fastest_all_counts[algo]}}}"
        fastest_all_macros.append(macro)
    for algo in ['b', 'c', 'c+', 'd']:
        macro = f"\\DefMacro{{fastest-all-percent-{algo}}}{{{fastest_all_counts[algo] / projects_count * 100:.1f}}}"
        fastest_all_macros.append(macro)
    return fastest_all_macros


def make_fastest_threshold_all_macros(fastest_threshold_all_counts, threshold):
    fastest_threshold_all_macros = []
    projects_count = sum(fastest_threshold_all_counts.values())
    for algo in ['b', 'c', 'd', 'all']:
        algoname = algo.replace('+','plus')
        macro = f"\\DefMacro{{fastest-count-{threshold}s-all-{algoname}}}{{{fastest_threshold_all_counts[algo]}}}"
        fastest_threshold_all_macros.append(macro)
    for algo in ['b', 'c', 'd', 'all']:
        macro = f"\\DefMacro{{fastest-count-{threshold}s-all-percent-{algo}}}{{{fastest_threshold_all_counts[algo] / projects_count * 100:.1f}}}"
        fastest_threshold_all_macros.append(macro)
    return fastest_threshold_all_macros


def main(args):
    data = load(args)
    macros = summarize_per_percentile(args, data)
    with open(os.path.join('algos-comparison-overhead-fastest-macros.tex'), mode = 'w') as f:
        f.writelines([str(x) + '\n' for x in macros])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate macros')
    parser.add_argument('overheadalgo')
    args = parser.parse_args()
    main(args)
