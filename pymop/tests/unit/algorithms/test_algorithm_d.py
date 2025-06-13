from typing import List
import pytest
import os

from pythonmop.monitor.algorithm_d import AlgorithmD
from pythonmop.monitor.monitor_d import MonitorD
from pythonmop.spec.data import SpecParameter

full_path = os.path.join(os.path.dirname(__file__))


def parse_event_line(event_line: str):
    # Extract the event name and the string for the parameters combination from the event line.
    event_name, params_str = event_line.strip().split(': ')

    # Special case for null parameter (event applied to all parameters).
    if params_str == '(,':
        return event_name, ''

    params = params_str.split(';')

    return event_name, params


def read_trace_file(file_path: str) -> List[str]:
    lines = []

    # Read the content from the file and return it.
    with open(file_path, 'r') as trace_file:
        lines = trace_file.readlines()

    return lines


def create_default_monitor(*, creation_events: List[str] = ["e1"]) -> MonitorD:
    handler = lambda: None
    monitor = MonitorD(
        'e1 e2 e3 e4 e5',
        creation_events,
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

    monitor.testing = True
    return monitor

def classFactory(className):
    return type(className, (object,), {
        '__init__': lambda self, *args, **kwargs: None,
        'get_name': lambda self: className
    })


def get_param_dict_to_spec_param_tuple():
    parameterTypes = {}
    parameterInstances = {}

    def param_dict_to_spec_param_tuple(param_to_param_instance_dict):
        spec_params = []
        param_type_names = param_to_param_instance_dict.keys()
        for param_type_name in param_type_names:
            if param_type_name not in parameterTypes:
                parameterTypes[param_type_name] = classFactory(param_type_name)
            
            instance_id = param_to_param_instance_dict[param_type_name]
            if instance_id not in parameterInstances:
                parameterInstances[instance_id] = parameterTypes[param_type_name]()

            spec_param = SpecParameter(instance_id, parameterTypes[param_type_name])
            spec_params.append(spec_param)

        return tuple(spec_params)

    return param_dict_to_spec_param_tuple

def convert_spec_param_tuple_list_to_str_tuple_list(spec_param_tuple_list):
    return [tuple(str(param) for param in spec_param_tuple) for spec_param_tuple in spec_param_tuple_list]


class TestAlgorithmD:

    @pytest.fixture
    def algo_d(self):
        FSM = ""
        return AlgorithmD("Test", FSM, ["Test"], {"e1": set(frozenset())})

    # ====================== is_compatible doesn't exist anymore in AlgorithmD ======================

    # def test_is_compatible_empty_params(self, algo_d):
    #     processing_params = {}
    #     current_params = {'param1': 'value1', 'param2': 'value2'}
    #     result = algo_d.is_compatible(processing_params, current_params)
    #     assert result is True

    # def test_is_compatible_same_params(self, algo_d):
    #     processing_params = {'param1': 'value1', 'param2': 'value2'}
    #     current_params = {'param1': 'value1', 'param2': 'value2'}
    #     result = algo_d.is_compatible(processing_params, current_params)
    #     assert result is True

    # def test_is_compatible_different_values(self, algo_d):
    #     processing_params = {'param1': 'value1', 'param2': 'value2'}
    #     current_params = {'param1': 'value1', 'param2': 'different_value'}
    #     result = algo_d.is_compatible(processing_params, current_params)
    #     assert result is False

    # def test_is_compatible_different_keys(self, algo_d):
    #     processing_params = {'param1': 'value1', 'param2': 'value2'}
    #     current_params = {'param1': 'value1', 'param3': 'value3'}
    #     result = algo_d.is_compatible(processing_params, current_params)
    #     assert result is True

    # ====================== ----------------------- ======================

    def test_case_possible_sub_params_with_self_1(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {
            'a': '1',
            'b': '1',
            'c': '1'
        }
        expected_result = [
            ('a-1', 'b-1', 'c-1'),
            ('a-1', 'b-1'),
            ('a-1', 'c-1'),
            ('b-1', 'c-1'),
            ('a-1',),
            ('b-1',),
            ('c-1',),
            ()
        ]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    True
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_with_self_2(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {
            'a': '1',
            'b': '1',
            'c': '1',
            'd': '1'
        }
    
        expected_result = [
            ('a-1', 'b-1', 'c-1', 'd-1'),
            ('a-1', 'b-1', 'c-1'),
            ('a-1', 'b-1', 'd-1'),
            ('a-1', 'c-1', 'd-1'),
            ('b-1', 'c-1', 'd-1'),
            ('a-1', 'b-1'),
            ('a-1', 'c-1'),
            ('a-1', 'd-1'),
            ('b-1', 'c-1'),
            ('b-1', 'd-1'),
            ('c-1', 'd-1'),
            ('a-1',),
            ('b-1',),
            ('c-1',),
            ('d-1',),
            ()
        ]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    True
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_with_self_empty(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {}
        expected_result = [()]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    True
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_without_self_1(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {
            'a': '1',
            'b': '1',
            'c': '1'
        }
        expected_result = [
            ('a-1', 'b-1'),
            ('a-1', 'c-1'),
            ('b-1', 'c-1'),
            ('a-1',),
            ('b-1',),
            ('c-1',),
            ()
        ]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    False
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_without_self_2(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {
            'a': '1',
            'b': '1',
            'c': '1',
            'd': '1'
        }

        expected_result = [
            ('a-1', 'b-1', 'c-1'),
            ('a-1', 'b-1', 'd-1'),
            ('a-1', 'c-1', 'd-1'),
            ('b-1', 'c-1', 'd-1'),
            ('a-1', 'b-1'),
            ('a-1', 'c-1'),
            ('a-1', 'd-1'),
            ('b-1', 'c-1'),
            ('b-1', 'd-1'),
            ('c-1', 'd-1'),
            ('a-1',),
            ('b-1',),
            ('c-1',),
            ('d-1',),
            ()
        ]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    False
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_without_self_empty(self, algo_d):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {}
        expected_result = []

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            list(
                algo_d.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example),
                    False
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_compute_enables(self):
        # Arrange
        expected_result = {
            'e1': {frozenset()},
            'e2': {frozenset({'e1'})},
            'e3': {frozenset({'e1', 'e2'})},
            'e4': {frozenset({'e1', 'e2', 'e3'})},
            'e5': {frozenset({'e1', 'e2', 'e3', 'e4'})}
        }

        # Act
        monitor = create_default_monitor()

        # Assert
        assert monitor.enable_map == expected_result

    def test_case_convert_enables(self):
        # Arrange
        expected_result = {
            'e1': {frozenset()},
            'e2': {frozenset({'a'})},
            'e3': {frozenset({'a', 'b'})},
            'e4': {frozenset({'a', 'b', 'c'})},
            'e5': {frozenset({'a', 'b', 'c', 'd'})}
        }

        # Act
        monitor = create_default_monitor()

        # Assert
        assert monitor.enable_map_parameters == expected_result
