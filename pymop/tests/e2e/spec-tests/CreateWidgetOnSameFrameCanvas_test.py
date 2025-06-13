from nltk.draw.util import CanvasFrame, CanvasWidget, SequenceWidget
from tkinter import Tk

class CircleWidget(CanvasWidget):
    def __init__(self, canvas, x, y, radius):
        self._circle_id = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="blue")
        super().__init__(canvas)
    
    def _tags(self):
        return (str(self._circle_id),)

class SimpleTextWidget(CanvasWidget):
    def __init__(self, canvas, text):
        self._text_id = canvas.create_text(10, 10, anchor="nw", text=text, fill="black")
        super().__init__(canvas)
    
    def __repr__(self):
        return "<SimpleTextWidget>"
    
    def _tags(self):
        return (str(self._text_id),)


def test_ok_1():
    assert True == True, "Should be true"

def test_ok_2():
    root = Tk()
    cf = CanvasFrame(root, width=400, height=200)
    canvas = cf.canvas()

    text_widget = SimpleTextWidget(canvas, "Hello, NLTK Canvas!")
    circle_widget = CircleWidget(canvas, 100, 100, 20)

    sequence_widget = SequenceWidget(canvas, text_widget, circle_widget, align='center', space=10)

    cf.add_widget(sequence_widget)


def test_violation_1():
    root = Tk()
    cf_1 = CanvasFrame(root, width=400, height=200)
    cf_2 = CanvasFrame(root, width=200, height=400)
    canvas_1 = cf_1.canvas()
    canvas_2 = cf_2.canvas()

    text_widget = SimpleTextWidget(canvas_1, "Hello, NLTK Canvas!")
    circle_widget = CircleWidget(canvas_2, 100, 100, 20)

    sequence_widget = SequenceWidget(canvas_2, text_widget, circle_widget, align='center', space=10)

    cf_1.add_widget(sequence_widget)

def test_violation_2():
    root = Tk()
    cf_1 = CanvasFrame(root, width=400, height=200)
    cf_2 = CanvasFrame(root, width=200, height=400)
    canvas_1 = cf_1.canvas()
    canvas_2 = cf_2.canvas()

    circle_widget_1 = CircleWidget(canvas_1, 100, 100, 20)
    circle_widget_2 = CircleWidget(canvas_2, 100, 100, 20)

    cf_1.add_widget(canvaswidget=circle_widget_1)
    cf_1.add_widget(canvaswidget=circle_widget_2)

def test_violation_3():
    root = Tk()
    cf_1 = CanvasFrame(root, width=400, height=200)
    cf_2 = CanvasFrame(root, width=200, height=400)
    canvas_1 = cf_1.canvas()
    canvas_2 = cf_2.canvas()

    circle_widget_2 = CircleWidget(canvas_2, 100, 100, 20)

    # this will throw an error because there isn't at least one canvasWidget on the canvas of CanvasFrame
    cf_1.add_widget(canvaswidget=circle_widget_2)

expected_violations_A = 3
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3]
