# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import re
import warnings


"""
    RegexpTokenizer pattern must not contain capturing parentheses
    src: https://www.nltk.org/api/nltk.tokenize.regexp.html
"""


def contains_capturing_groups(pattern):
    regex = re.compile(pattern)

    if regex.groups > 0:
        # Further check to distinguish capturing from non-capturing by examining the pattern
        # This involves checking all group occurrences in the pattern
        # We need to avoid matching escaped parentheses \( or \) and non-capturing groups (?: ...)
        non_capturing = re.finditer(r'\(\?[:=!]', pattern)
        non_capturing_indices = {match.start() for match in non_capturing}
        
        # Finding all parentheses that could start a group
        all_groups = re.finditer(r'\((?!\?)', pattern)
        for match in all_groups:
            if match.start() not in non_capturing_indices:
                return True  # Found at least one capturing group
        return False
    else:
        return False


class NLTK_RegexpTokenizerCapturingParentheses(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["RegexpTokenizer"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["nltk.tokenize.regexp.RegexpTokenizer"]

        # Get the class name
        if hasattr(function, '__module__') and hasattr(function, '__name__'):
            class_name = function.__module__ + "." + function.__name__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            pattern = None
            if kw_args.get('pattern'):
                pattern = kw_args['pattern']
            elif len(pos_args) > 1:
                pattern = pos_args[1]

            # Check if the regular expression is empty
            if pattern is not None and contains_capturing_groups(pattern):
                # Add the event to the event dictionary
                if "regexpTokenizerCreated" not in self.event:
                    self.event["regexpTokenizerCreated"] = 1
                else:
                    self.event["regexpTokenizerCreated"] += 1

                # Add the violation to the violation dictionary
                self.violation += 1

                # Find the file name and line number of the function in the original file
                call_file_name = dyn_ast
                call_line_num = BaseAnalysis.iid_to_location(self, dyn_ast, iid).start_line

                # Add the violation to the unique violation dictionary
                violation_key = f'{call_file_name}:{call_line_num}'
                if violation_key not in self.unique_event:
                    self.unique_event[violation_key] = 1
                    self.unique_violation += 1  # Increment the unique violation count
                else:
                    self.unique_event[violation_key] += 1

                # Print the violation message
                warnings.warn(
                    f'Spec - {self.__class__.__name__}: Must use non_capturing parentheses for RegexpTokenizer pattern. '
                    f'File {call_file_name}, line {call_line_num}.')

    def end_execution(self) -> None:
        # Count the number of events
        event_count = 0
        for key in self.event:
            event_count += self.event[key]

        # Write the statistics to a file
        with open(f'{self.__class__.__name__}_statistics.txt', 'w') as f:
            f.write(f"DynaPyt_Event_Count: {event_count}\n")
            f.write(f'DynaPyt_Event: {self.event}\n')
            f.write(f'DynaPyt_Unique_Event: {self.unique_event}\n')
            f.write(f"DynaPyt_Violation_Count: {self.violation}\n")
            f.write(f"DynaPyt_Unique_Violation_Count: {self.unique_violation}\n")
# =========================================================================
