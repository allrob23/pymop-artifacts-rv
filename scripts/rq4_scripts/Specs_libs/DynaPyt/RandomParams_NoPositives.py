# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    random.lognormvariate(mu, sigma) -> mu can have any value, and sigma must be greater than zero.
    random.vonmisesvariate(mu, kappa) ->  kappa must be greater than or equal to zero.
"""


class RandomParams_NoPositives(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["lognormvariate", "vonmisesvariate"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["random"]

        # Get the class name
        if hasattr(function, '__module__'):
            class_name = function.__module__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            violation = False
            if function.__name__ == "lognormvariate":
                sigma = None
                if kw_args.get('sigma'):
                    sigma = kw_args['sigma']
                elif len(pos_args) > 1:
                    sigma = pos_args[1]

                if sigma is not None and sigma <= 0:
                    violation = True

            else:  # Must be vonmisesvariate in this case
                kappa = None
                if kw_args.get('kappa'):
                    kappa = kw_args['kappa']
                elif len(pos_args) > 1:
                    kappa = pos_args[1]

                if kappa is not None and kappa < 0:
                    violation = True

            if violation:
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
                    f'Spec - {self.__class__.__name__}: The call to method lognormvariate or vonmisesvariate in file {call_file_name} at line {call_line_num} does not have the correct parameters.')

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
