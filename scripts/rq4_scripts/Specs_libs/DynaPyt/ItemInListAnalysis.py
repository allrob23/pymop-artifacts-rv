# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis

import warnings


class ItemInListAnalysis(BaseAnalysis):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

        self.threshold = 100
        self.count = 5
        self.size_map = {}

    def _in(self, dyn_ast, iid, left, right, result):
        if type(right) == list and len(right) > self.threshold:
            uid = id(right)
            if uid not in self.size_map:
                self.size_map[uid] = len(right)
            else:
                self.size_map[uid] += len(right)
            if self.size_map[uid] > self.threshold * self.count:
                # Add the event to the event dictionary
                if "list_contains" not in self.event:
                    self.event["list_contains"] = 1
                else:
                    self.event["list_contains"] += 1

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
                    f'Spec - {self.__class__.__name__}: Searching for an item in a long list is not efficient. Consider using a set at file {call_file_name}, line {call_line_num}.')

    def not_in(self, dyn_ast, iid, left, right, result):
        self._in(dyn_ast, iid, left, right, result)

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
