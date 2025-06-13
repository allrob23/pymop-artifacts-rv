# ============================== Define spec ==============================
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only

from typing import Callable, Tuple, Dict
import warnings


"""
    This specification ensures that canvas widgets are added only to the CanvasFrame's designated canvas
    source: https://www.nltk.org/api/nltk.draw.util.html#nltk.draw.util.CanvasFrame.add_widget
"""


class CreateWidgetOnSameFrameCanvas(BaseAnalysis):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.event = {}
        self.unique_event = {}
        self.violation = 0
        self.unique_violation = 0

    @only(patterns=["add_widget"])
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        # The target class names for monitoring
        targets = ["nltk.draw.util.CanvasFrame"]

        # Get the class name
        if hasattr(function, '__self__') and hasattr(function.__self__, '__class__'):
            cls = function.__self__.__class__
            class_name = cls.__module__ + "." + cls.__name__
        else:
            class_name = None

        # Check if the class name is the target ones
        if class_name in targets:

            # Spec content
            args = pos_args
            kwargs = kw_args

            canvasFrame = function.__self__  # Updated to use the self object
            canvasWidget = None

            if len(args) > 1:
                canvasWidget = args[1]
            else:
                canvasWidget = kwargs['canvaswidget']

            fCanvas = canvasFrame.canvas()
            wCanvas = canvasWidget.canvas()

            # TODO: Do we need to recursively check the children of the CanvasWidget?
            # Logically, it makes sense, but docs don't mention it directly.

            if wCanvas.winfo_id() != fCanvas.winfo_id():

                # Add the event to the event dictionary
                if "widgetAdded" not in self.event:
                    self.event["widgetAdded"] = 1
                else:
                    self.event["widgetAdded"] += 1

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
                    f'Spec - {self.__class__.__name__}: CanvasWidget must be created on the same canvas as the CanvasFrame it is being added to.'
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
