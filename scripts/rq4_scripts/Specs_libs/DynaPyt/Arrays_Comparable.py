# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    This specification ensures that the elements of an array are comparable before sorting them.
    Source: https://docs.python.org/3/library/functions.html#sorted.
"""


class Arrays_Comparable(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["sorted"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["builtins"]

        # Get the class name
        if hasattr(function, '__module__'):
            class_name = function.__module__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            objs = pos_args[0]
            if isinstance(objs, list):
                new_objs = objs[:]  # Shallow copy the elements in the list inputted.
                if kw_args.get('key'):  # If a key method for comparison is provided.
                    key = kw_args['key']  # Store the key method.
                    for i in range(len(new_objs)):  # Convert the elements using the inputted key method.
                        new_objs[i] = key(new_objs[i])
                try:  # Check if the object is comparable.
                    for i in range(len(new_objs)):
                        for j in range(i + 1, len(new_objs)):
                            # This will raise a TypeError if elements at i and j are not comparable.
                            _ = new_objs[i] < new_objs[j]
                except TypeError:
                    # Add the event to the event dictionary
                    if "invalid_sorted" not in self.event:
                        self.event["invalid_sorted"] = 1
                    else:
                        self.event["invalid_sorted"] += 1

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
                        f'Spec - {self.__class__.__name__}: Array with non-comparable elements is about to be sorted. '
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
