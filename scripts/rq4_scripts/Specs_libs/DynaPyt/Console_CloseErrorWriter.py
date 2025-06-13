# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    This specification warns if close() is invoked on sys.stderr which is a useless invocation.
    Source: https://docs.python.org/3/faq/library.html#why-doesn-t-closing-sys-stdout-stdin-stderr-really-close-it.
"""


class Console_CloseErrorWriter(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["close"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["<stderr>"]

        # Get the class name
        if hasattr(function, '__self__') and hasattr(function.__self__, 'name'):
            class_name = function.__self__.name
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:
            # Add the event to the event dictionary
            if "close" not in self.event:
                self.event["close"] = 1
            else:
                self.event["close"] += 1

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
                f'Spec - {self.__class__.__name__}: The close() method does not necessarily need to be called on sys.stderr. '
                f'(violation at file {call_file_name}, line {call_line_num}).')

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
