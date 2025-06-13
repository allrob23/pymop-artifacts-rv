import pytest

from pythonmop.monitor.algorithm_c import AlgorithmC
from pythonmop.spec.data import SpecParameter

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

class TestAlgorithmC:

    @pytest.fixture
    def algo_c(self):
        return AlgorithmC("test")

    def test_is_compatible_empty_params(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()
        processing_params = {}
        current_params = {'param1': 'value1', 'param2': 'value2'}
        result = algo_c.is_compatible(param_dict_to_spec_param_tuple(processing_params), param_dict_to_spec_param_tuple(current_params))
        assert result is True

    def test_is_compatible_same_params(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        processing_params = {'param1': 'value1', 'param2': 'value2'}
        current_params = {'param1': 'value1', 'param2': 'value2'}

        result = algo_c.is_compatible(param_dict_to_spec_param_tuple(processing_params), param_dict_to_spec_param_tuple(current_params))

        assert result is True

    def test_is_compatible_different_values(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        processing_params = {'param1': 'value1', 'param2': 'value2'}
        current_params = {'param1': 'value1', 'param2': 'different_value'}

        result = algo_c.is_compatible(param_dict_to_spec_param_tuple(processing_params), param_dict_to_spec_param_tuple(current_params))

        assert result is False

    def test_is_compatible_different_keys(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        processing_params = {'param1': 'value1', 'param2': 'value2'}
        current_params = {'param1': 'value1', 'param3': 'value3'}

        result = algo_c.is_compatible(param_dict_to_spec_param_tuple(processing_params), param_dict_to_spec_param_tuple(current_params))

        assert result is True

    def test_case_possible_sub_params_1(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        param_type_to_instance_id_dict = {
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
                algo_c.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(param_type_to_instance_id_dict)
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_2(self, algo_c):
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
                algo_c.find_possible_sub_params(
                    param_dict_to_spec_param_tuple(test_example)
                )
            )
        )

        # Assert
        assert result == expected_result

    def test_case_possible_sub_params_empty(self, algo_c):
        param_dict_to_spec_param_tuple = get_param_dict_to_spec_param_tuple()

        # Arrange
        test_example = {}
        expected_result = [()]

        # Act
        result = convert_spec_param_tuple_list_to_str_tuple_list(
            algo_c.find_possible_sub_params(
                param_dict_to_spec_param_tuple(test_example)
            )
        )

        # Assert
        assert result == expected_result
