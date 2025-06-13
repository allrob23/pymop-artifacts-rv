# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Any, Callable, Dict, Tuple
import builtins
import warnings

class BuiltinAllAnalysis(BaseAnalysis):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    def _flatten(self, l):
        new_list = []
        for i in l:
            if isinstance(i, list):
                new_list = new_list + self._flatten(i)
            else:
                new_list.append(i)
        return new_list

    @only(patterns=["all", "any"])
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
        if function == builtins.all or function == builtins.any:
            arg = pos_args[0]
            if isinstance(arg, list):
                flattened = self._flatten(arg)
                if len(flattened) == 0 and val == True:
                    # Add the event to the event dictionary
                    if "violation" not in self.event:
                        self.event["violation"] = 1
                    else:
                        self.event["violation"] += 1

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
                        f'Spec - {self.__class__.__name__}: Potentially unintended result for any() call at file {call_file_name}, line {call_line_num}.')
                    
    
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
