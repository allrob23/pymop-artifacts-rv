from pathlib import Path
import fire

here = Path(__file__).parent.resolve()

issue_codes = {
    "PC-05": {
        "name": "ItemInList",
        "analysis": "dylin.analyses.ItemInListAnalysis.ItemInListAnalysis",
        "aliases": [],
    },
    "PC-06": {
        "name": "FilesClosed",
        "analysis": "dylin.analyses.FilesClosedAnalysis.FilesClosedAnalysis",
        "aliases": ["A-08"],
    },
    "SL-02": {
        "name": "AnyAllMisuse",
        "analysis": "dylin.analyses.BuiltinAllAnalysis.BuiltinAllAnalysis",
        "aliases": ["A-21"],
    },
    "TE-02": {
        "name": "Arrays_Comparable",
        "analysis": "dylin.analyses.Arrays_Comparable.Arrays_Comparable",
        "aliases": ["B-1"],
    },
    "TE-03": {
        "name": "Console_CloseErrorWriter",
        "analysis": "dylin.analyses.Console_CloseErrorWriter.Console_CloseErrorWriter",
        "aliases": ["B-2"],
    },
    "TE-04": {
        "name": "Console_CloseReader",
        "analysis": "dylin.analyses.Console_CloseReader.Console_CloseReader",
        "aliases": ["B-3"],
    },
    "TE-05": {
        "name": "Console_CloseWriter",
        "analysis": "dylin.analyses.Console_CloseWriter.Console_CloseWriter",
        "aliases": ["B-4"],
    },
    "TE-06": {
        "name": "CreateWidgetOnSameFrameCanvas",
        "analysis": "dylin.analyses.CreateWidgetOnSameFrameCanvas.CreateWidgetOnSameFrameCanvas",
        "aliases": ["B-5"],
    },
    "TE-07": {
        "name": "HostnamesTerminatesWithSlash",
        "analysis": "dylin.analyses.HostnamesTerminatesWithSlash.HostnamesTerminatesWithSlash",
        "aliases": ["B-6"],
    },
    "TE-08": {
        "name": "NLTK_regexp_span_tokenize",
        "analysis": "dylin.analyses.NLTK_regexp_span_tokenize.NLTK_regexp_span_tokenize",
        "aliases": ["B-8"],
    },
    "TE-09": {
        "name": "NLTK_RegexpTokenizerCapturingParentheses",
        "analysis": "dylin.analyses.NLTK_RegexpTokenizerCapturingParentheses.NLTK_RegexpTokenizerCapturingParentheses",
        "aliases": ["B-9"],
    },
    "TE-10": {
        "name": "PriorityQueue_NonComparable",
        "analysis": "dylin.analyses.PriorityQueue_NonComparable.PriorityQueue_NonComparable",
        "aliases": ["B-10"],
    },
    "TE-11": {
        "name": "PyDocs_MustOnlyAddSynchronizableDataToSharedList",
        "analysis": "dylin.analyses.PyDocs_MustOnlyAddSynchronizableDataToSharedList.PyDocs_MustOnlyAddSynchronizableDataToSharedList",
        "aliases": ["B-11"],
    },
    "TE-12": {
        "name": "RandomParams_NoPositives",
        "analysis": "dylin.analyses.RandomParams_NoPositives.RandomParams_NoPositives",
        "aliases": ["B-12"],
    },
    "TE-13": {
        "name": "RandomRandrange_MustNotUseKwargs",
        "analysis": "dylin.analyses.RandomRandrange_MustNotUseKwargs.RandomRandrange_MustNotUseKwargs",
        "aliases": ["B-13"],
    },
    "TE-14": {
        "name": "Requests_DataMustOpenInBinary",
        "analysis": "dylin.analyses.Requests_DataMustOpenInBinary.Requests_DataMustOpenInBinary",
        "aliases": ["B-14"],
    },
    "TE-15": {
        "name": "Session_DataMustOpenInBinary",
        "analysis": "dylin.analyses.Session_DataMustOpenInBinary.Session_DataMustOpenInBinary",
        "aliases": ["B-15"],
    },
    "TE-16": {
        "name": "Sets_Comparable",
        "analysis": "dylin.analyses.Sets_Comparable.Sets_Comparable",
        "aliases": ["B-16"],
    },
    "TE-17": {
        "name": "socket_create_connection",
        "analysis": "dylin.analyses.socket_create_connection.socket_create_connection",
        "aliases": ["B-17"],
    },
    "TE-18": {
        "name": "socket_setdefaulttimeout",
        "analysis": "dylin.analyses.socket_setdefaulttimeout.socket_setdefaulttimeout",
        "aliases": ["B-18"],
    },
    "TE-19": {
        "name": "socket_socket_settimeout",
        "analysis": "dylin.analyses.socket_socket_settimeout.socket_socket_settimeout",
        "aliases": ["B-19"],
    },
    "TE-20": {
        "name": "Thread_OverrideRun",
        "analysis": "dylin.analyses.Thread_OverrideRun.Thread_OverrideRun",
        "aliases": ["B-20"],
    },
}


def select_checkers(include: str = "all", exclude: str = "none", output_dir: str = None) -> str:
    if include is None:
        include = "none"
    if exclude is None:
        exclude = "none"
    if include.lower() == "all" and exclude.lower() == "none":
        res = "\n".join([issue["analysis"] for _, issue in issue_codes.items()])
    elif include.lower() == "all":
        res = "\n".join(
            [
                issue["analysis"]
                for code, issue in issue_codes.items()
                if (code not in exclude and issue["name"] not in exclude)
            ]
        )
    elif exclude.lower() == "none":
        res = "\n".join(
            [issue["analysis"] for code, issue in issue_codes.items() if (code in include or issue["name"] in include)]
        )
    else:
        res = "\n".join(
            [
                issue["analysis"]
                for code, issue in issue_codes.items()
                if (code in include or issue["name"] in include)
                and (code not in exclude and issue["name"] not in exclude)
            ]
        )
    if output_dir is not None:
        return "\n".join([f"{ana};output_dir={output_dir}" for ana in res.split("\n")])
    return res


if __name__ == "__main__":
    fire.Fire(select_checkers)
