# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Any, Callable, Tuple, Dict
import warnings


class StringStripAnalysis(BaseAnalysis):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["strip"])
    def post_call(
        self,
        dyn_ast: str,
        iid: int,
        val: Any,
        function: Callable,
        pos_args: Tuple,
        kw_args: Dict,
    ) -> Any:
        # print(f"{self.analysis_name} post_call {iid}")
        if val is function:
            return
        _self = getattr(function, "__self__", lambda: None)

        if not isinstance(_self, str):
            return
        
        # Declare violation as False for easier specification
        violation = False

        if len(pos_args) > 0 and not _self is None and function == _self.strip:
            arg = pos_args[0]
            _self = function.__self__
            if len(set(arg)) != len(arg):
                violation = True  # Violation is true if the argument contains duplicates
            if len(arg) > 1 and (
                (_self.startswith(arg) and _self[len(arg) : len(arg) + 1] in arg)
                or (_self.endswith(arg) and _self[-len(arg) - 1 : -len(arg)] in arg)
            ):
                violation = True  # Violation is true if the argument contains duplicates

        if violation:
            # Add the event to the event dictionary
            if "string_strip" not in self.event:
                self.event["string_strip"] = 1
            else:
                self.event["string_strip"] += 1

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
                f'Spec - {self.__class__.__name__}: Possible misuse of str.strip, arg contains duplicates {arg}. '
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
