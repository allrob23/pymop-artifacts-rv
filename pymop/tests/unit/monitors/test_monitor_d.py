import pytest
from typing import Any, List
import os

from pythonmop.monitor.monitor_d import MonitorD
from pythonmop.spec.data import SpecParameter
from pythonmop.monitor.formalismhandler.base import Base

traces_dir_path = f'{os.path.join(os.path.dirname(__file__))}/../test-data/traces/'

Base.save_event_history = True

def parse_event_line(event_line: str):
    # Extract the event name and the string for the parameters combination from the event line.
    event_name, params_str = event_line.strip().split(': ')

    # Special case for null parameter (event applied to all parameters).
    if params_str == '(,':
        return event_name, ''

    param_instances = [{
        'type': full_param_name.split('-')[0].strip(),
        'id': full_param_name.split('-')[1].strip()
    } for full_param_name in params_str.replace(';', '').split(',')]

    return event_name, param_instances


def read_trace_file(file_path: str) -> List[str]:
    lines = []

    # Read the content from the file and return it.
    with open(file_path, 'r') as trace_file:
        lines = trace_file.readlines()

    return lines

def hadler_fake_func():
    pass

def classFactory(className):
    return type(className, (object,), {
        '__init__': lambda self, *args, **kwargs: None,
        'get_name': lambda self: className
    })


def getParametricTrace(file_path: str):
    traces = read_trace_file(file_path)

    parameter_types = {}
    parameter_instances = {}

    parametric_trace = [] # list of tuples (event, [tuple of SpecParameter])
    refs = []

    for trace in traces:
        event, param_instances_str = parse_event_line(trace)

        affected_params = []
        for param_instance in param_instances_str:
            param_type = param_instance['type']
            param_id = param_instance['id']
            param_instance_id = f'{param_type}-{param_id}'

            if param_type not in parameter_types:
                parameter_types[param_type] = classFactory(param_type)
            
            if param_instance_id not in parameter_instances:
                parameter_instances[param_instance_id] = parameter_types[param_type]()
                refs.append(parameter_instances[param_instance_id])
            
            param_object = SpecParameter(id=param_id, param_type=Any if parameter_types[param_type] is None else parameter_types[param_type])
            affected_params.append(param_object)

        parametric_trace.append((event, tuple(affected_params)))

    return parametric_trace, refs

def fake_handler(event, *args):
    pass

def create_new_monitor() -> MonitorD:
    handler = lambda: None
    return MonitorD(
        'e1 e2 e3 e4 e5',
        ['e1'],
        [
            'e1',
            'e2',
            'e3',
            'e4',
            'e5'
        ],
        "ere",
        {
            "e1": "a",
            "e2": "b",
            "e3": "c",
            "e4": "d",
            "e5": "e"
        },
        {'violation': handler},
        "Test"
    )

algo_d_data = [
    {
        'trace_file': 'trace_test13.txt',
        'expected_result': {
            'a-1': ['e1'],
            'a-1,b-1': ['e1', 'e2']
        }
    }
]

test_data = [
    (test_case['trace_file'], test_case['expected_result']) for test_case in algo_d_data
]

class TestMonitorD:
    @pytest.mark.parametrize('trace_file, expected_result', test_data)
    def test_monitor_d_against_trace_file(self, trace_file, expected_result):
        print(f'Running D on {trace_file}.')
        monitor = create_new_monitor()

        parametric_trace, refs = getParametricTrace(f'{traces_dir_path}/{trace_file}')

        for event, params in parametric_trace:
            monitor.update_params_handler(event, [params], refs, '', 0, None, None)

        result = monitor.params_monitors.get_event_history()

        assert result == expected_result
    
    def test_ere_monitor_creation(self):
        # Arrange
        formula = 'getInstance update (update* reset* update* digest)*'
        events = ['getInstance', 'update', 'reset', 'digest']
        formalism = 'ere'
        handlers = {}

        # Act
        test_monitor = MonitorD(
            formula,
            [""],
            events,
            formalism,
            {
                "getInstance": "a",
                "update": "b",
                "reset": "c",
                "digest": "d"
            },
            handlers,
            "Test"
        )
        test_fsm = test_monitor.get_fsm()

        # Expectations
        expected_current_state = 's0'
        expected_transitions = {
            's0': {'getInstance': 's1'},
            's1': {'update': 's2'},
            's2': {'update': 's3', 'reset': 's4', 'digest': 's2'},
            's3': {'update': 's3', 'reset': 's4', 'digest': 's2'},
            's4': {'update': 's5', 'reset': 's4', 'digest': 's2'},
            's5': {'update': 's5', 'digest': 's2'}
        }
        expected_alias_sections = {'match': ['s2']}

        # Assert
        assert test_fsm.current_state == expected_current_state
        assert test_fsm.transitions == expected_transitions
        assert test_fsm.alias_sections == expected_alias_sections
    
    def test_ere_monitor_success_transition(self):
        # Arrange
        formula = 'getInstance update (update* reset* update* digest)*'
        events = ['getInstance', 'update', 'reset', 'digest']
        formalism = 'ere'
        handlers = {}

        # Act
        test_monitor = MonitorD(
            formula,
            ["getInstance"],
            events,
            formalism,
            {
                "getInstance": "a",
                "update": "b",
                "reset": "c",
                "digest": "d"
            },
            handlers,
            "Test"
        )
        test_monitor.params_monitors.fsm_index_tree = {"": test_monitor.fsm}
        test_monitor.transit_state('getInstance', '', 'filename', 0, '', [], {})
        test_monitor.transit_state('update', '', 'filename', 0, '', [], {})

    def test_ere_monitor_fail_transition(self):
        # Arrange
        formula = 'getInstance update (update* reset* update* digest)*'
        events = ['getInstance', 'update', 'reset', 'digest']
        formalism = 'ere'
        handlers = {}

        # Act
        test_monitor = MonitorD(
            formula,
            ["getInstance"],
            events,
            formalism,
            {
                "getInstance": "a",
                "update": "b",
                "reset": "c",
                "digest": "d"
            },
            handlers, "Test"
        )
        test_monitor.params_monitors.fsm_index_tree = {"": test_monitor.fsm}
        test_monitor.transit_state('getInstance', '', 'filename', 0, '', [], {})
        test_monitor.transit_state('getInstance', '', 'filename', 0, '', [], {})

    def test_ltl_monitor_fail_transition(self):
        # Arrange
        formula = '[](create => o (explicit or implicit))'  # fromTempFile
        events = ['create', 'implicit', 'explicit']
        formalism = 'ltl'
        handlers = {}
        parameter_event_map = {'default': [], 'implicit': [], 'explicit': [], 'create': []}

        # Act
        test_monitor = MonitorD(formula, ["create"], events, formalism, parameter_event_map, handlers, "Test")
        test_monitor.params_monitors.fsm_index_tree = {"": test_monitor.fsm}
        test_monitor.transit_state('create', '', 'filename', 0, '', [], {})
        test_monitor.transit_state('implicit', '', 'filename', 0, '', [], {})

    def test_ltl_monitor_fail_transition2(self):
        # Arrange
        formula = '[](next => (*) hasnexttrue)'  # from StringTokenizer
        events = ['next', 'hasnextfalse', 'hasnexttrue']
        formalism = 'ltl'
        handlers = {}
        parameter_event_map = {'default': [], 'hasnextfalse': [], 'hasnexttrue': [], 'next': []}

        # Act
        test_monitor = MonitorD(formula, ["next"], events, formalism, parameter_event_map, handlers, "Test")
        test_monitor.params_monitors.fsm_index_tree = {"": test_monitor.fsm}
        test_monitor.transit_state('next', '', 'filename', 0, '', [], {})
        test_monitor.transit_state('hasnextfalse', '', 'filename', 0, '', [], {})

    def test_fsm_monitor_fail_transition(self):
        # Arrange
        formula = """
        s0 [
getInstance -> s1
]
s1 [
update -> s2
]
s2 [
update -> s3
reset -> s4
digest -> s2
]
s3 [
update -> s3
reset -> s4
digest -> s2
]
s4 [
update -> s5
reset -> s4
digest -> s2
]
s5 [
update -> s5
digest -> s2
]
alias match = s2
            """
        events = ['getInstance', 'update', 'reset', 'digest']
        formalism = 'fsm'
        handlers = {'match': fake_handler}

        # Act
        parameter_event_map = {'default': []}
        for event_name in events:
            if event_name not in parameter_event_map.keys():
                parameter_event_map[event_name] = []

        test_monitor = MonitorD(formula, ["getInstance"], events, formalism, parameter_event_map, handlers, "Test")
        test_monitor.params_monitors.fsm_index_tree = {"": test_monitor.fsm}
        test_monitor.transit_state('getInstance', '', 'filename', 0, '', [], {})
        test_monitor.transit_state('getInstance', '', 'filename', 0, '', [], {})

    def test_exception_in_monitor_creation(self):
        # Arrange
        formula = """
        s0 [
            getInstance -> s1
        ]
        s1 [
            update -> s2
        ]
        s2 [
            update -> s3
            reset -> s4
            digest -> s2
        ]
        
        alias match = s2
                """
        events = ['getInstance', 'update', 'reset', 'digest']
        formalism = 'wrong_formalism'
        handlers = {}

        # Act
        with pytest.raises(Exception) as exc_info:
            test_monitor = MonitorD(formula, ["getInstance"], events, formalism, {"": ""}, handlers, "Test")

        assert f'ERROR: The formalism "{formalism}" is not supported by the tool!' in str(exc_info.value)