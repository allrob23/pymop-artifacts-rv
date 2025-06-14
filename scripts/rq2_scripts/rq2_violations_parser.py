import pandas as pd


"""
Script to parse the violation locations from the test results
"""

file_path = "results.csv"

# Load the result dataset for the comparison experiment
data = pd.read_csv(file_path)

def parse_total_violations(val):
    if val == "x":
        return 0
    else:
        return int(val)
    
def parse_violations(val):
    if val == "x":
        return ""
    elif val != "" and type(val) == str:
        new_violations = []
        print(val)
        for item in val.split(";"):
            if item != "":
                spec, count = item.split("=")
                new_violations.append(spec + "=" + count)
        return ";".join(new_violations)
    else:
        return ""

def parse_unique_violations_count(val):
    if val == "x" or pd.isna(val):
        return ""
    elif val != "":
        new_count = []
        print(val)
        for item in val.split(";"):
            if item != "":
                spec, count = item.split("=")
                new_count.append(spec + "=" + count)
        return ";".join(new_count)
    return ""

def parse_violations_by_location(val):
    if val == "x" or pd.isna(val):
        return ""
    elif val != "":
        new_count = []
        for item in val.split(";"):
            if item != "":
                file, count = item.split("=")
                if "PyMOP_ast" in file:
                    file = file.split("PyMOP_ast")[1]
                elif "PyMOP_curses" in file:
                    file = file.split("PyMOP_curses")[1]
                elif "PyMOP_monkey" in file:
                    file = file.split("PyMOP_monkey")[1]
                new_count.append(file + "=" + count)
        return ";".join(new_count)
    return ""

# Apply standardization
for col, func in [
    ("total_violations", parse_total_violations),
    ("unique_violations_count", parse_unique_violations_count),
    ("violations", parse_violations),
    ("violations_by_location", parse_violations_by_location),
]:
    if col in data.columns:
        data[col] = data[col].apply(func)

# Save the result to a new csv file
output_path = file_path.replace('.csv', '_processed.csv')
data.to_csv(output_path, index=False)
