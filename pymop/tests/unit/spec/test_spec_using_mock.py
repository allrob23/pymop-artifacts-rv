import pytest

from pythonmop import BaseInstrumentTarget, BaseParameterDeclaration, SpecParameter
from pythonmop.spec import spec
from pythonmop.monitor.monitor_d import MonitorD

from typing import Dict, Callable, Any
import inspect
from pythonmop import Spec

import pythonmop.spec.spec as spec_all
spec_all.DONT_MONITOR_PYTHONMOP = False

ALGOS = ["A", "B", "C", "C+", "D"]


# Example class to test instrumentation
@pytest.fixture
def mock_class():
    class MockClass:
        def mock_func(self, num: int):
            return num + 10

    return MockClass


# Mock Monitor which stores all events in event_trace
class MockMonitor(MonitorD):
    def __init__(self, formula, events, formalism, handlers):
        self.formula = formula
        self.events = events
        self.formalism = formalism
        self.handlers = handlers
        self.event_trace = []  # all events will just be stored here

    def transit_state(self, event_name, param, filename, line_num, custom_message, args, kwargs):
        self.event_trace.append((event_name, filename, line_num, args, kwargs))

    def update_params_handler(self, event_name, params, param_refs, filename, line_num, custom_message, *args, **kwargs):
        self.event_trace.append((event_name, filename, line_num, *args, *kwargs))


def test_get_instrumented_func(mock_class):
    # Create base spec
    spec_instance = Spec()

    # Instrument example class
    setattr(
        mock_class,
        'mock_func',
        spec._get_instrumented_func(
            mock_class.mock_func,
            "spec_test",
            type(mock_class.mock_func)
        )
    )

    # Check that event-type lists have been added
    assert hasattr(mock_class.mock_func, 'pythonmop_before_event_types')
    assert hasattr(mock_class.mock_func, 'pythonmop_after_event_types')

    # Add event-types
    spec_instance.monitor = MockMonitor(None, None, None, None)

    before_event_hook_args = None

    def before_event_hook(**kwargs):
        nonlocal before_event_hook_args
        before_event_hook_args = kwargs

    before_event_type = spec._EventType('before_event', spec_instance, before_event_hook)
    mock_class.mock_func.pythonmop_before_event_types.append(before_event_type)

    after_event_hook_args = None

    def after_event_hook(**kwargs):
        nonlocal after_event_hook_args
        after_event_hook_args = kwargs

    after_event_type = spec._EventType('after_event', spec_instance, after_event_hook)
    mock_class.mock_func.pythonmop_after_event_types.append(after_event_type)

    # Call instrumented function and check return value
    mock_class_instance = mock_class()
    return_val = mock_class_instance.mock_func(15)
    call_line_num = inspect.currentframe().f_lineno - 1
    call_file_name = __file__
    assert return_val == 25

    # Check event trace
    assert spec_instance.monitor.event_trace == [
        ('before_event', call_file_name, call_line_num, (mock_class_instance, 15), {}),
        ('after_event', call_file_name, call_line_num, (mock_class_instance, 15), {})]

    # Check event hook arguments

    assert before_event_hook_args['func_name'] == 'mock_func'
    assert before_event_hook_args['kwargs'] == {}

    assert after_event_hook_args['return_val'] == 25
    assert after_event_hook_args['kwargs'] == {}


def test_instrumented_func_event_order(mock_class):
    setattr(
        mock_class,
        'mock_func',
        spec._get_instrumented_func(
            mock_class.mock_func,
            "spec_test",
            type(mock_class.mock_func)
        )
    )

    spec_instance = Spec()
    spec_instance.monitor = MockMonitor(None, None, None, None)

    before_event_hook_args = []
    before_event_hook_event_order = []

    def before_event_hook(**kwargs):
        before_event_hook_args.append(kwargs)
        before_event_hook_event_order.append(kwargs['func_name'])

    before_event_type = spec._EventType('before_event', spec_instance, before_event_hook)
    mock_class.mock_func.pythonmop_before_event_types.append(before_event_type)

    after_event_hook_args = []
    after_event_hook_event_order = []

    def after_event_hook(**kwargs):
        after_event_hook_args.append(kwargs)
        after_event_hook_event_order.append(kwargs['func_name'])

    after_event_type = spec._EventType('after_event', spec_instance, after_event_hook)
    mock_class.mock_func.pythonmop_after_event_types.append(after_event_type)

    return_val = mock_class().mock_func(15)

    assert len(before_event_hook_args) == len(after_event_hook_args) == 1
    assert before_event_hook_args[0]['func_name'] == 'mock_func'
    assert after_event_hook_args[0]['func_name'] == 'mock_func'
    assert before_event_hook_event_order == after_event_hook_event_order == ['mock_func']


def test_instrumented_func_event_args(mock_class):
    setattr(mock_class, 'mock_func', spec._get_instrumented_func(mock_class.mock_func, "spec_test",
                                                                 type(mock_class.mock_func)))

    spec_instance = Spec()
    spec_instance.monitor = MockMonitor(None, None, None, None)

    before_event_hook_args = []

    def before_event_hook(**kwargs):
        before_event_hook_args.append(kwargs)

    before_event_type = spec._EventType('before_event', spec_instance, before_event_hook)
    mock_class.mock_func.pythonmop_before_event_types.append(before_event_type)

    after_event_hook_args = []

    def after_event_hook(**kwargs):
        after_event_hook_args.append(kwargs)

    after_event_type = spec._EventType('after_event', spec_instance, after_event_hook)
    mock_class.mock_func.pythonmop_after_event_types.append(after_event_type)

    return_val = mock_class().mock_func(15)

    # Add assert statements here once we implement argument extraction from function calls:
    # before_event_hook_args[0]['args'] = (<tests.unit.spec.test_spec_using_mock.mock_class.<locals>.MockClass object at 0x125ef26f0>,
    #  15)
    assert before_event_hook_args[0]['args'][1] == 15
    assert after_event_hook_args[0]['args'][1] == 15
    assert before_event_hook_args[0]['kwargs'] == {}
    assert after_event_hook_args[0]['kwargs'] == {}


def test_instrumented_func_event_exceptions(mock_class):
    setattr(mock_class, 'mock_func', spec._get_instrumented_func(mock_class.mock_func, "spec_test",
                                                                 type(mock_class.mock_func)))

    spec_instance = Spec()
    spec_instance.monitor = MockMonitor(None, None, None, None)

    before_event_hook_args = []

    def before_event_hook(**kwargs):
        before_event_hook_args.append(kwargs)

    before_event_type = spec._EventType('before_event', spec_instance, before_event_hook)
    mock_class.mock_func.pythonmop_before_event_types.append(before_event_type)

    after_event_hook_args = []

    def after_event_hook(**kwargs):
        after_event_hook_args.append(kwargs)

    after_event_type = spec._EventType('after_event', spec_instance, after_event_hook)
    mock_class.mock_func.pythonmop_after_event_types.append(after_event_type)

    try:
        mock_class().mock_func("invalid_argument")
    except Exception as e:
        pass

    assert before_event_hook_args[0]['exception'] is None
    assert after_event_hook_args[0]['exception'] is not None
    assert isinstance(after_event_hook_args[0]['exception'], Exception)


# Spec tests

class MockInstrumentTarget(BaseInstrumentTarget):
    pass


class MockParameterDeclaration(BaseParameterDeclaration):
    pass


def mock_hook(**kw):
    a = 10
    b = 30


def test_instrument_event_before_hooks(monkeypatch, mock_class):
    # Arrange
    instance = Spec()
    namespace = mock_class
    instance.create_monitor = lambda: None
    instance.monitor = None
    instance.namespace = namespace
    event_args = [MockInstrumentTarget(namespace, 'mock_func')]
    before = True

    # Act
    instance._instrument_event(mock_hook, event_args, before)
    return_val = namespace().mock_func(15)

    # Assert
    assert return_val == 25
    assert hasattr(namespace.mock_func, 'pythonmop_before_event_types')
    assert hasattr(namespace.mock_func, 'pythonmop_after_event_types')


def test_instrument_event_after_hooks(monkeypatch, mock_class):
    instance = Spec()
    namespace = mock_class
    instance.create_monitor = lambda: None
    instance.monitor = None
    instance.namespace = namespace
    event_args = [MockInstrumentTarget(namespace, 'mock_func')]
    before = False

    # Act
    instance._instrument_event(mock_hook, event_args, before)
    return_val = namespace().mock_func(15)

    # Assert
    assert return_val == 25
    assert hasattr(namespace.mock_func, 'pythonmop_before_event_types')
    assert hasattr(namespace.mock_func, 'pythonmop_after_event_types')


# Monitor tests
class MockSpec(Spec):
    def __init__(self, formal_exp=None, fsm=None, ere=None, ltl=None, violation=None, match=None):
        super().__init__()
        self.formal_exp = formal_exp
        self.fsm = fsm
        self.ere = ere
        self.ltl = ltl
        self.violation = violation
        self.match = match
        self.monitor = None


def test_create_monitor_with_no_formal_expression():
    for i in ALGOS:
        # Arrange
        spec_instance = MockSpec()

        # Act
        spec_instance.create_monitor(i)

        # Assert
        assert spec_instance.monitor is None


def test_create_monitor_with_non_string_formal_expression():
    for i in ALGOS:
        # Arrange
        spec_instance = MockSpec(formal_exp=123)

        # Act
        spec_instance.create_monitor(i)

        # Assert
        assert spec_instance.monitor is None


def test_param_without_type():
    # Arrange
    spec_instance = MockSpec()

    # Act
    param = spec_instance.param(0, list)

    # Assert
    assert isinstance(param, SpecParameter)
    assert param.id == 0
    assert param.param_type == list



def test_param_with_type():
    # Arrange
    spec_instance = Spec()

    # Act
    param = spec_instance.param(0, int)

    # Assert
    assert isinstance(param, SpecParameter)
    assert param.id == 0
    assert param.param_type == int


def test_param_with_multiple_calls():
    # Arrange
    spec_instance = Spec()

    # Act
    param1 = spec_instance.param(0, int)
    param2 = spec_instance.param(1, str)

    # Assert
    assert isinstance(param1, SpecParameter)
    assert isinstance(param2, SpecParameter)
    assert param1.id == 0
    assert param2.id == 1
    assert param1.param_type == int
    assert param2.param_type == str


# Event tests
def test_event_before_decorator(mock_class):
    # Arrange
    spec_instance = Spec()
    namespace = mock_class
    hook_called = False

    # Act
    @spec_instance.event_before(MockInstrumentTarget(namespace, 'mock_func'))
    def hook(**kw):
        nonlocal hook_called
        hook_called = True

    spec_instance.create_monitor("D")
    return_val = namespace().mock_func(15)

    # Assert
    assert return_val == 25
    assert hook_called
    assert hasattr(namespace.mock_func, 'pythonmop_before_event_types')
    assert hasattr(namespace.mock_func, 'pythonmop_after_event_types')


def test_event_after_decorator(mock_class):
    # Arrange
    spec_instance = Spec()
    namespace = mock_class
    hook_called = False

    # Act
    @spec_instance.event_after(MockInstrumentTarget(namespace, 'mock_func'))
    def hook(**kw):
        nonlocal hook_called
        hook_called = True

    spec_instance.create_monitor("D")
    return_val = namespace().mock_func(15)

    # Assert
    assert return_val == 25
    assert hook_called
    assert hasattr(namespace.mock_func, 'pythonmop_before_event_types')
    assert hasattr(namespace.mock_func, 'pythonmop_after_event_types')
