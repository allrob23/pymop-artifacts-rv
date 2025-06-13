# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Any, Callable, Dict, Tuple
import warnings
import builtins

"""
Name: 
EnsureFilesClosed

Source:
-

Test description:
Ensures that every file created with `open('filename')` is closed before termination.
Recommended usage is using `with`.
Even though CPython uses reference counting which will close the file other python interpreters like
IronPython, PyPy, and Jython do not use reference counting.  

Why useful in a dynamic analysis approach:
Non trivial control flows can not be analysed properly by static analysis and thus miss a correct / missing close operation

Discussion:


"""


class FilesClosedAnalysis(BaseAnalysis):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0
        self.files = {}

    @only(patterns=["open"])
    def post_call(
        self,
        dyn_ast: str,
        iid: int,
        res: Any,
        function: Callable,
        pos_args: Tuple,
        kw_args: Dict,
    ) -> Any:
        if function == builtins.open:
            if id(res) not in self.files:
                # id works here because we keep file into memory
                # could be optimized to use obj mirror though
                self.files[id(res)] = (iid, res, dyn_ast)

    def end_execution(self) -> None:
        for id in self.files:
            try:
                if not self.files[id][1].closed:
                    # Add the event to the event dictionary
                    if "file_not_closed" not in self.event:
                        self.event["file_not_closed"] = 1
                    else:
                        self.event["file_not_closed"] += 1

                    # Add the violation to the violation dictionary
                    self.violation += 1

                    # Find the file name and line number of the function in the original file
                    call_file_name = self.files[id][2]
                    call_line_num = BaseAnalysis.iid_to_location(self, self.files[id][2], self.files[id][0]).start_line

                    # Add the violation to the unique violation dictionary
                    violation_key = f'{call_file_name}:{call_line_num}'
                    if violation_key not in self.unique_event:
                        self.unique_event[violation_key] = 1
                        self.unique_violation += 1  # Increment the unique violation count
                    else:
                        self.unique_event[violation_key] += 1

                    # Print the violation message
                    warnings.warn(
                        f'Spec - {self.__class__.__name__}: You forgot to close the file at file {call_file_name}, line {call_line_num}.')
            except AttributeError:
                pass

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
