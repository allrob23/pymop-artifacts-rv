# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    It is strongly recommended that you open files in binary mode. This is because Requests may attempt to provide
    the Content-Length header for you, and if it does this value will be set to the number of bytes in the file.
    Errors may occur if you open the file in text mode.
"""


class Requests_DataMustOpenInBinary(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["post"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["requests.api"]

        # Get the class name
        if hasattr(function, '__module__'):
            class_name = function.__module__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            kwords = ['data', 'files']
            for k in kwords:
                if k in kw_args:
                    data = kw_args[k]
                    if hasattr(data, 'read') and hasattr(data, 'mode') and 'b' not in data.mode:

                        # Add the event to the event dictionary
                        if "test_verify" not in self.event:
                            self.event["test_verify"] = 1
                        else:
                            self.event["test_verify"] += 1

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
                            f'Spec - {self.__class__.__name__}: It is strongly recommended that you open files in binary mode. This '
                            f'is because Requests may attempt to provide the Content-Length header for you, and if it does this value '
                            f'will be set to the number of bytes in the file. Errors may occur if you open the file in text mode. in '
                            f'{call_file_name} at line {call_line_num}')

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
