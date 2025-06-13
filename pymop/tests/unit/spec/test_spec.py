import pytest

from pythonmop import BaseInstrumentTarget, SpecParameter, MonitorD
from pythonmop.monitor.monitor_d import MonitorD
from typing import Any
from pythonmop import Spec, call
import re
import os
import math
import bisect

import pythonmop.spec.spec as spec_all
spec_all.DONT_MONITOR_PYTHONMOP = False

# Example class to test instrumentation
@pytest.fixture
def mock_class():
    class MockClass:
        def mock_func(self, num: int):
            return num + 10

    return MockClass

def create_new_monitor():
    # Add event-types
    monitor_ = MonitorD(
        formula='getInstance update (update* reset* update* digest)*',
        creation_events=['getInstance'],
        events=['getInstance', 'update', 'reset', 'digest'],
        formalism='ere',
        parameter_event_map={
            "": [""]
        },
        handlers={},
        spec_name="Test"
    )

    return monitor_

def test_instrumented_func_event_order(mock_class):
    # Define example spec
    class ExampleSpec(Spec):
        def __init__(self):
            self.before_event_hook_args = []
            self.before_event_hook_event_order = []
            self.parameter_event_map = {'default': [], 'before_event': [], 'after_event': []}

            @self.event_before(call(mock_class, 'mock_func'))
            def before_event(**kwargs):
                self.before_event_hook_args.append(kwargs)
                self.before_event_hook_event_order.append(kwargs['func_name'])

            self.after_event_hook_args = []
            self.after_event_hook_event_order = []

            @self.event_after(call(mock_class, 'mock_func'))
            def after_event(**kwargs):
                self.after_event_hook_args.append(kwargs)
                self.after_event_hook_event_order.append(kwargs['func_name'])

    # Apply example spec
    spec = ExampleSpec()
    spec.create_monitor("D")

    # Call instrumented function
    return_val = mock_class().mock_func(15)

    # Check results
    assert len(spec.before_event_hook_args) == len(spec.after_event_hook_args) == 1
    assert spec.before_event_hook_args[0]['func_name'] == 'mock_func'
    assert spec.after_event_hook_args[0]['func_name'] == 'mock_func'
    assert spec.before_event_hook_event_order == spec.after_event_hook_event_order == ['mock_func']

def test_instrumented_func_event_args(mock_class):
    # Define example spec
    class ExampleSpec(Spec):
        def __init__(self):
            self.before_event_hook_args = []
            self.parameter_event_map = {'default': [], 'before_event': [], 'after_event': []}


            @self.event_before(call(mock_class, 'mock_func'))
            def before_event(**kwargs):
                self.before_event_hook_args.append(kwargs)

            self.after_event_hook_args = []

            @self.event_after(call(mock_class, 'mock_func'))
            def after_event(**kwargs):
                self.after_event_hook_args.append(kwargs)

    # Apply example spec
    spec = ExampleSpec()
    spec.create_monitor("D")

    # Call instrumented function
    mock_instance_self = mock_class()
    return_val = mock_instance_self.mock_func(15)

    # Check function call arguments
    assert return_val == 25
    assert spec.before_event_hook_args[0]['args'] == (mock_instance_self, 15,)
    assert spec.after_event_hook_args[0]['args'] == (mock_instance_self, 15,)
    assert spec.before_event_hook_args[0]['kwargs'] == {}
    assert spec.after_event_hook_args[0]['kwargs'] == {}

def test_instrumented_func_event_exceptions(mock_class):
    class ExampleSpec(Spec):
        def __init__(self):
            self.before_event_hook_args = []
            self.parameter_event_map = {'default': [], 'before_event': [], 'after_event': []}


            @self.event_before(call(mock_class, 'mock_func'))
            def before_event(**kwargs):
                self.before_event_hook_args.append(kwargs)

            self.after_event_hook_args = []

            @self.event_after(call(mock_class, 'mock_func'))
            def after_event(**kwargs):
                self.after_event_hook_args.append(kwargs)

    # Apply example spec
    spec = ExampleSpec()
    spec.create_monitor("D")  # as we have no formal expression defined, it will create a "empty" monitor
    spec.monitor = 123        # so we need it (to avoid empty monitor) to have the exception key

    user_exception = None
    try:
        mock_class().mock_func("invalid_argument")
    except Exception as e:
        user_exception = e

    assert spec.before_event_hook_args[0]['exception'] is None
    assert spec.after_event_hook_args[0]['exception'] is not None
    assert user_exception is spec.after_event_hook_args[0]['exception']
    assert isinstance(spec.after_event_hook_args[0]['exception'], Exception)

class MockInstrumentTarget(BaseInstrumentTarget):
    pass

## ======================================== Spec tests with monitorD ==========================================
class MockSpec(Spec):
    def __init__(self, formal_exp=None, fsm=None, ere=None, ltl=None, violation=None, match=None, event_names=None):
        super().__init__()
        self.formal_exp = formal_exp
        self.fsm = fsm
        self.ere = ere
        self.ltl = ltl
        self.violation = violation
        self.match = match
        self.event_names = event_names
        self.MonitorD = None
        self.creation_events = []

def test_create_monitor_with_fsm_and_violation_handlers():
    # Arrange
    fsm_expr = """start [
                      default start
                      next -> unsafe
                      hasnext -> safe
                   ]
                   safe [
                      next -> start
                      hasnext -> safe 
                   ]
                   unsafe [
                      next -> unsafe
                      hasnext -> safe
                   ]
                   alias all_states = start, safe, unsafe
                   alias safe_states = start, safe"""
    violation_handler = lambda: None
    spec_instance = MockSpec(fsm=fsm_expr, violation=violation_handler, event_names=['start', 'safe', 'unsafe', 'hasnext', 'next'])

    # Act
    spec_instance.create_monitor("D")

    # Assert
    assert isinstance(spec_instance.monitor, MonitorD)
    assert spec_instance.monitor.formalism == "fsm"
    assert "violation" in spec_instance.monitor.error_handlers
    assert "match" not in spec_instance.monitor.error_handlers

def test_create_monitor_with_ere_and_match_handlers():
    # Arrange
    ere_expr = "(sync asyncCreateIter) | (sync syncCreateIter accessIter)"
    match_handler = lambda: None
    spec_instance = MockSpec(ere=ere_expr, match=match_handler,
                             event_names=['sync', 'asyncCreateIter', 'syncCreateIter', 'accessIter'])

    # Act
    spec_instance.create_monitor("D")

    # Assert
    assert isinstance(spec_instance.monitor, MonitorD)
    assert spec_instance.monitor.formalism == "ere"
    assert "match" in spec_instance.monitor.error_handlers
    assert "violation" not in spec_instance.monitor.error_handlers

def test_create_monitor_with_no_formal_expression():
    # Arrange
    spec_instance = MockSpec()

    # Act
    assert spec_instance.create_monitor("D") is None

def test_create_monitor_with_non_string_formal_expression():
    # Arrange
    spec_instance = MockSpec(formal_exp=123)

    # Act and Assert
    assert spec_instance.create_monitor("D") is None

def test_param_without_type():
    # Arrange
    spec_instance = Spec()

    # Act
    param = spec_instance.param(10)

    # Assert
    assert isinstance(param, SpecParameter)
    assert param.id == 10
    assert param.param_type == Any

def test_param_with_type():
    # Arrange
    spec_instance = Spec()

    # Act
    param = spec_instance.param(0,int)

    # Assert
    assert isinstance(param, SpecParameter)
    assert param.id == 0
    assert param.param_type == int

def test_param_with_multiple_calls():
    # Arrange
    spec_instance = Spec()

    # Act
    param1 = spec_instance.param(0, int)
    param2 = spec_instance.param(1, int)

    # Assert
    assert isinstance(param1, SpecParameter)
    assert isinstance(param2, SpecParameter)
    assert param1.id == 0
    assert param2.id == 1
    assert param1.param_type == int
    assert param2.param_type == int

## ========================================== Event tests ==========================================
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


## ========================================== TEST REGEX METHODS ==========================================

def test_methods_ending_in_all_in_re_namespace():
    s = Spec()
    regex_pattern = r'.*all$'
    matched_methods = s._get_regex_function_name(re, regex_pattern)
    expected_methods = ['findall']
    assert sorted(matched_methods) == sorted(expected_methods)

def test_methods_containing_path_in_os_namespace():
    s = Spec()
    regex_pattern = r'.*path.*'
    matched_methods = s._get_regex_function_name(os, regex_pattern)
    expected_methods = ['_fspath', 'fpathconf', 'fspath', 'get_exec_path', 'pathconf']
    assert sorted(matched_methods) == sorted(expected_methods)

def test_methods_starting_with_is_or_log_in_math_namespace():
    s = Spec()
    regex_pattern = r'^(is|log).*'
    matched_methods = s._get_regex_function_name(math, regex_pattern)
    expected_methods = ['isclose', 'isfinite', 'isinf', 'isnan', 'isqrt', 'log', 'log10', 'log1p', 'log2']
    assert sorted(expected_methods) == sorted(expected_methods)

def test_methods_from_bisect():
    s = Spec()
    regex_pattern = 'bisect.*'
    matched_methods = s._get_regex_function_name(bisect, regex_pattern)
    expected_methods = ['bisect', 'bisect_left', 'bisect_right']
    assert sorted(matched_methods) == sorted(expected_methods)
