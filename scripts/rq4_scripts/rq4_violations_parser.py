import pandas as pd


"""
Script to parse the violation locations from the test results
"""

file_path = "results.csv"

# Load the result dataset for the comparison experiment
data = pd.read_csv(file_path)

spec_dict = {"PC-05": "ItemInListAnalysis",
             "PC-06": "FilesClosedAnalysis",
             "SL-02": "AnyAllMisuseAnalysis",
             "TE-02": "Arrays_Comparable",
             "TE-03": "Console_CloseErrorWriter",
             "TE-04": "Console_CloseReader",
             "TE-05": "Console_CloseWriter",
             "TE-06": "CreateWidgetOnSameFrameCanvas",
             "TE-07": "HostnamesTerminatesWithSlash",
             "TE-08": "NLTK_regexp_span_tokenize",
             "TE-09": "NLTK_RegexpTokenizerCapturingParentheses",
             "TE-10": "PriorityQueue_NonComparable",
             "TE-11": "PyDocs_MustOnlyAddSynchronizableDataToSharedList",
             "TE-12": "RandomParams_NoPositives",
             "TE-13": "RandomRandrange_MustNotUseKwargs",
             "TE-14": "Requests_DataMustOpenInBinary",
             "TE-15": "Session_DataMustOpenInBinary",
             "TE-16": "Sets_Comparable",
             "TE-17": "socket_create_connection",
             "TE-18": "socket_setdefaulttimeout",
             "TE-19": "socket_socket_settimeout",
             "TE-20": "Thread_OverrideRun"}

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
                new_violations.append(item)
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
                if spec in spec_dict.keys():
                    new_count.append(spec_dict[spec] + "=" + count)
                else:
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
                if "PyMOP" in file:
                    file = file.split("PyMOP")[1]
                elif "DynaPyt" in file:
                    file = file.split("DynaPyt")[1]
                    file = "".join(file.split(".orig"))
                elif "DyLin" in file:
                    file = file.split("DyLin")[1]
                    file = "".join(file.split(".orig"))
                elif "DynaPyt_Libs" in file:
                    file = file.split("DynaPyt_Libs")[1]
                    file = "".join(file.split(".orig"))
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
