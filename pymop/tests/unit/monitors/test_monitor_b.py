import pytest
from typing import Any, List
import os

from pythonmop.monitor.monitor_b import MonitorB
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

def create_new_monitor():
    return MonitorB('start start+', ['start'], 'ere', {}, {}, "test")

algo_b_data = [
    {
        # used in the paper "Parametric Trace Slicing and Monitoring" as example
        'trace_file': 'trace_test1.txt',
        'expected_result': {
            '': ['e6'],
            'a-1': ['e1', 'e5', 'e6'],
            'a-2': ['e2', 'e6'],
            'a-2,b-1': ['e2', 'e3', 'e4', 'e6', 'e7'],
            'a-1,b-1': ['e1', 'e3', 'e5', 'e6', 'e7'],
            'b-1': ['e3', 'e6', 'e7']
        }
    },
    {
        'trace_file': 'trace_test2.txt',
        'expected_result': {
            '':            ['e6', 'e11'],
            'a-1':         ['e1', 'e5', 'e6', 'e11'],
            'a-2':         ['e2', 'e6', 'e11'],
            'a-2,b-1':     ['e2', 'e3', 'e4', 'e6', 'e7', 'e11'],
            'a-1,b-1':     ['e1', 'e3', 'e5', 'e6', 'e7', 'e11'],
            'b-1':         ['e3', 'e6', 'e7', 'e11'],
            'b-1,c-1':     ['e3', 'e6', 'e7', 'e8', 'e11'],
            'a-1,b-1,c-1': ['e1', 'e3', 'e5', 'e6', 'e7', 'e8', 'e10', 'e11'],
            'a-2,b-1,c-1': ['e2', 'e3', 'e4', 'e6', 'e7', 'e8', 'e9', 'e11'],
            'a-2,c-1':     ['e2', 'e6', 'e8', 'e9', 'e11'],
            'a-1,c-1':     ['e1', 'e5', 'e6', 'e8', 'e11'],
            'c-1':         ['e6', 'e8', 'e11']
        }
    },
    {
        'trace_file': 'trace_test3.txt',
        'expected_result': {
            '':            ['e1', 'e11'],
            'a-1':         ['e1', 'e2', 'e11', 'e12'],
            'b-1':         ['e1', 'e3', 'e11'],
            'a-1,b-1':     ['e1', 'e2', 'e3', 'e11', 'e12', 'e13'],
            'c-1':         ['e1', 'e4', 'e11'],
            'b-1,c-1':     ['e1', 'e3', 'e4', 'e11'],
            'a-1,c-1':     ['e1', 'e2', 'e4', 'e11', 'e12'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e4', 'e9', 'e11', 'e12', 'e13'],
            'a-2':         ['e1', 'e5', 'e8', 'e11'],
            'a-2,b-1':     ['e1', 'e3', 'e5', 'e8', 'e10', 'e11'],
            'a-2,c-1':     ['e1', 'e4', 'e5', 'e8', 'e11'],
            'a-2,b-1,c-1': ['e1', 'e3', 'e4', 'e5', 'e8', 'e10', 'e11'],
            'a-3':         ['e1', 'e6', 'e11'],
            'a-3,c-1':     ['e1', 'e4', 'e6', 'e11'],
            'a-3,b-1':     ['e1', 'e3', 'e6', 'e11'],
            'a-3,b-1,c-1': ['e1', 'e3', 'e4', 'e6', 'e11'],
            'c-2':         ['e1', 'e7', 'e11'],
            'a-2,c-2':     ['e1', 'e5', 'e7', 'e8', 'e11'],
            'a-3,c-2':     ['e1', 'e6', 'e7', 'e11'],
            'a-1,c-2':     ['e1', 'e2', 'e7', 'e11', 'e12'],
            'b-1,c-2':     ['e1', 'e3', 'e7', 'e11'],
            'a-3,b-1,c-2': ['e1', 'e3', 'e6', 'e7', 'e11'],
            'a-2,b-1,c-2': ['e1', 'e3', 'e5', 'e7', 'e8', 'e10', 'e11'],
            'a-1,b-1,c-2': ['e1', 'e2', 'e3', 'e7', 'e11', 'e12', 'e13']
        }
    },
    {
        'trace_file': 'trace_test4.txt',
        'expected_result': {
            '':            [],
            'a-1':         ['e1', 'e3'],
            'a-1,c-1':     ['e1', 'e2', 'e3'],
            'c-1':         ['e2'],
            'a-1,b-1':     ['e1', 'e3', 'e4'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e4'],
            'b-1':         ['e4'],
            'b-1,c-1':     ['e2', 'e4']
        }
    },
    {
        'trace_file': 'trace_test5.txt',
        'expected_result': {
            '':            ['e5', 'e6'],
            'a-1':         ['e1', 'e5', 'e6', 'e7'],
            'a-1,c-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8'],
            'c-1':         ['e2', 'e4', 'e5', 'e6', 'e8'],
            'a-1,c-2':     ['e1', 'e5', 'e6', 'e7', 'e9'],
            'c-2':         ['e5', 'e6', 'e9'],
            'b-3':         ['e5', 'e6', 'e10'],
            'a-1,b-3,c-2': ['e1', 'e5', 'e6', 'e7', 'e9', 'e10'],
            'a-1,b-3':     ['e1', 'e5', 'e6', 'e7', 'e10'],
            'b-3,c-1':     ['e2', 'e4', 'e5', 'e6', 'e8', 'e10'],
            'b-3,c-2':     ['e5', 'e6', 'e9', 'e10'],
            'a-1,b-3,c-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e10']
        }
    },
    {
        'trace_file': 'trace_test6.txt',
        'expected_result': {
            '':            ['e1', 'e7', 'e8'],
            'c-1':         ['e1', 'e2', 'e6', 'e7', 'e8'],
            'b-2':         ['e1', 'e3', 'e7', 'e8', 'e9'],
            'b-2,c-1':     ['e1', 'e2', 'e3', 'e6', 'e7', 'e8', 'e9'],
            'a-1':         ['e1', 'e4', 'e7', 'e8'],
            'a-1,b-2,c-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9'],
            'a-1,c-1':     ['e1', 'e2', 'e4', 'e6', 'e7', 'e8'],
            'a-1,b-2':     ['e1', 'e3', 'e4', 'e5', 'e7', 'e8', 'e9']
        }
    },
    {
        'trace_file': 'trace_test7.txt',
        'expected_result': {
            '':            ['e1', 'e3', 'e4'],
            'a-1':         ['e1', 'e2', 'e3', 'e4', 'e5', 'e8'],
            'a-1,c-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8'],
            'c-1':         ['e1', 'e3', 'e4', 'e6'],
            'c-2':         ['e1', 'e3', 'e4', 'e9'],
            'a-1,c-2':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e8', 'e9'],
            'a-1,b-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e8', 'e10'],
            'b-1,c-2':     ['e1', 'e3', 'e4', 'e9', 'e10'],
            'b-1':         ['e1', 'e3', 'e4', 'e10'],
            'a-1,b-1,c-2': ['e1', 'e2', 'e3', 'e4', 'e5', 'e8', 'e9', 'e10'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e10'],
            'b-1,c-1':     ['e1', 'e3', 'e4', 'e6', 'e10']
        }
    },
    {
        'trace_file': 'trace_test8.txt',
        'expected_result': {
            '':            ['e1', 'e8'],
            'a-1':         ['e1', 'e2', 'e6', 'e8'],
            'b-1':         ['e1', 'e3', 'e7', 'e8'],
            'a-1,b-1':     ['e1', 'e2', 'e3', 'e6', 'e7', 'e8'],
            'a-2':         ['e1', 'e4', 'e8'],
            'a-2,b-1':     ['e1', 'e3', 'e4', 'e7', 'e8'],
            'a-1,b-2':     ['e1', 'e2', 'e5', 'e6', 'e8'],
            'a-2,b-2':     ['e1', 'e4', 'e5', 'e8'],
            'b-2':         ['e1', 'e5', 'e8'],
            'a-1,c-1':     ['e1', 'e2', 'e6', 'e8', 'e9'],
            'a-2,b-1,c-1': ['e1', 'e3', 'e4', 'e7', 'e8', 'e9'],
            'b-2,c-1':     ['e1', 'e5', 'e8', 'e9'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e6', 'e7', 'e8', 'e9'],
            'a-1,b-2,c-1': ['e1', 'e2', 'e5', 'e6', 'e8', 'e9'],
            'a-2,c-1':     ['e1', 'e4', 'e8', 'e9'],
            'b-1,c-1':     ['e1', 'e3', 'e7', 'e8', 'e9'],
            'c-1':         ['e1', 'e8', 'e9'],
            'a-2,b-2,c-1': ['e1', 'e4', 'e5', 'e8', 'e9']
        }
    },
    {
        'trace_file': 'trace_test9.txt',
        'expected_result': {
            '':                ['e1', 'e8'],
            'a-1':             ['e1', 'e2', 'e3', 'e4', 'e8', 'e9'],
            'd-1':             ['e1', 'e5', 'e8', 'e10'],
            'a-1,d-1':         ['e1', 'e2', 'e3', 'e4', 'e5', 'e8', 'e9', 'e10'],
            'f-1':             ['e1', 'e6', 'e8'],
            'a-1,f-1':         ['e1', 'e2', 'e3', 'e4', 'e6', 'e8', 'e9'],
            'a-1,d-1,f-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e8', 'e9', 'e10'],
            'd-1,f-1':         ['e1', 'e5', 'e6', 'e8', 'e10'],
            'a-1,d-1,f-1,g-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'e10'],
            'd-1,g-1':         ['e1', 'e5', 'e7', 'e8', 'e10'],
            'f-1,g-1':         ['e1', 'e6', 'e7', 'e8'],
            'a-1,d-1,g-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e7', 'e8', 'e9', 'e10'],
            'a-1,g-1':         ['e1', 'e2', 'e3', 'e4', 'e7', 'e8', 'e9'],
            'a-1,f-1,g-1':     ['e1', 'e2', 'e3', 'e4', 'e6', 'e7', 'e8', 'e9'],
            'd-1,f-1,g-1':     ['e1', 'e5', 'e6', 'e7', 'e8', 'e10'],
            'g-1':             ['e1', 'e7', 'e8']
        }
    },
    {
        'trace_file': 'trace_test10.txt',
        'expected_result': {
            '':            ['e1', 'e10'],
            'a-1':         ['e1', 'e2', 'e9', 'e10'],
            'b-1':         ['e1', 'e3', 'e6', 'e10'],
            'a-1,b-1':     ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e9', 'e10'],
            'a-1,b-2':     ['e1', 'e2', 'e7', 'e8', 'e9', 'e10'],
            'b-2':         ['e1', 'e7', 'e10']
        }
    },
    {
        'trace_file': 'trace_test11.txt',
        'expected_result': {
            '':        ['e6', 'e7'],
            'a-1':     ['e1', 'e6', 'e7', 'e8'],
            'a-2':     ['e2', 'e6', 'e7', 'e9'],
            'a-2,b-1': ['e2', 'e3', 'e6', 'e7', 'e9', 'e10'],
            'a-1,b-1': ['e1', 'e3', 'e6', 'e7', 'e8', 'e10'],
            'b-1':     ['e3', 'e6', 'e7', 'e10'],
            'a-3':     ['e4', 'e6', 'e7', 'e11'],
            'a-3,b-1': ['e3', 'e4', 'e6', 'e7', 'e10', 'e11'],
            'a-3,b-2': ['e4', 'e5', 'e6', 'e7', 'e11', 'e12'],
            'a-1,b-2': ['e1', 'e5', 'e6', 'e7', 'e8', 'e12'],
            'a-2,b-2': ['e2', 'e5', 'e6', 'e7', 'e9', 'e12'],
            'b-2':     ['e5', 'e6', 'e7', 'e12']
        }
    },
    {
        'trace_file': 'trace_test12.txt',
        'expected_result': {
            '':            ['e10'],
            'a-1':         ['e1', 'e4', 'e10'],
            'a-1,b-1':     ['e1', 'e2', 'e4', 'e5', 'e10'],
            'b-1':         ['e2', 'e5', 'e10'],
            'b-1,c-1':     ['e2', 'e3', 'e5', 'e6', 'e9', 'e10'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e9', 'e10'],
            'a-1,c-1':     ['e1', 'e3', 'e4', 'e6', 'e10'],
            'c-1':         ['e3', 'e6', 'e10'],
            'b-2':         ['e7', 'e10'],
            'b-2,c-1':     ['e3', 'e6', 'e7', 'e10'],
            'a-1,b-2,c-1': ['e1', 'e3', 'e4', 'e6', 'e7', 'e8', 'e10'],
            'a-1,b-2':     ['e1', 'e4', 'e7', 'e8', 'e10']
        }
    }
]

test_data = [
    (test_case['trace_file'], test_case['expected_result']) for test_case in algo_b_data
]

@pytest.mark.parametrize('trace_file, expected_result', test_data)
class TestAlgorithmB:
    def test_algo_b_against_trace_file(self, trace_file, expected_result):
        print(f'Running B on {trace_file}.')
        monitor = create_new_monitor()

        parametric_trace, refs = getParametricTrace(f'{traces_dir_path}/{trace_file}')

        for event, params in parametric_trace:
            monitor.update_params_handler(event, [params], refs, '', 0, '', None, None)

        assert monitor.params_monitors.get_event_history() == expected_result
