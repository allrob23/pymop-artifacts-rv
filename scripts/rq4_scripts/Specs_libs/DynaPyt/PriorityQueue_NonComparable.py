# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    This is used to check if PriorityQueue is about to have a non-comparable object.
"""


class PriorityQueue_NonComparable(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["put", "heappush"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["queue", "_heapq"]

        # Get the class name
        if hasattr(function, '__module__') and hasattr(function, '__name__'):
            class_name = function.__module__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            if function.__name__ == "put" and class_name == "queue" and hasattr(function, '__self__') and type(function.__self__).__name__ == "PriorityQueue":
                obj = pos_args[0]
                try:  # check if the object is comparable
                    obj < obj
                except TypeError as e:
                    # Add the event to the event dictionary
                    if "pq_put" not in self.event:
                        self.event["pq_put"] = 1
                    else:
                        self.event["pq_put"] += 1

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
                        f'Spec - {self.__class__.__name__}: PriorityQueue is about to have a non-comparable object. '
                        f'File {call_file_name}, line {call_line_num}.')

            if function.__name__ == "heappush" and class_name == "_heapq":
                obj = pos_args[1]
                try:  # check if the object is comparable
                    obj < obj
                except TypeError as e:
                    # Add the event to the event dictionary
                    if "heap_push" not in self.event:
                        self.event["heap_push"] = 1
                    else:
                        self.event["heap_push"] += 1

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
                        f'Spec - {self.__class__.__name__}: PriorityQueue is about to have a non-comparable object. '
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
