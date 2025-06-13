from pythonmop.monitor.algorithm_a import AlgorithmA
import os


traces_dir_path = f'{os.path.join(os.path.dirname(__file__))}/../test-data/traces/'

class TestAlgorithmA:

    def test_case_1(self):
        # used in the paper "Parametric Trace Slicing and Monitoring" as example
        expected_result = {
            '': ['e6'],
            'a-1': ['e1', 'e5', 'e6'],
            'a-2': ['e2', 'e6'],
            'a-2,b-1': ['e2', 'e3', 'e4', 'e6', 'e7'],
            'a-1,b-1': ['e1', 'e3', 'e5', 'e6', 'e7'],
            'b-1': ['e3', 'e6', 'e7']
        }

        a = AlgorithmA('test1', f'{traces_dir_path}/trace_test1.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_2(self):
        # used in the paper "SEMANTICS AND ALGORITHMS FOR PARAMETRIC MONITORING" as example
        expected_result = {
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

        a = AlgorithmA('test2', f'{traces_dir_path}/trace_test2.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_3(self):
        expected_result = {
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
    
        a = AlgorithmA('test3', f'{traces_dir_path}/trace_test3.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_4(self):
        expected_result = {
            '':            [],
            'a-1':         ['e1', 'e3'],
            'a-1,c-1':     ['e1', 'e2', 'e3'],
            'c-1':         ['e2'],
            'a-1,b-1':     ['e1', 'e3', 'e4'],
            'a-1,b-1,c-1': ['e1', 'e2', 'e3', 'e4'],
            'b-1':         ['e4'],
            'b-1,c-1':     ['e2', 'e4']
        }

        a = AlgorithmA('test4', f'{traces_dir_path}/trace_test4.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_5(self):
        expected_result = {
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

        a = AlgorithmA('test5', f'{traces_dir_path}/trace_test5.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_6(self):
        expected_result = {
            '':            ['e1', 'e7', 'e8'],
            'c-1':         ['e1', 'e2', 'e6', 'e7', 'e8'],
            'b-2':         ['e1', 'e3', 'e7', 'e8', 'e9'],
            'b-2,c-1':     ['e1', 'e2', 'e3', 'e6', 'e7', 'e8', 'e9'],
            'a-1':         ['e1', 'e4', 'e7', 'e8'],
            'a-1,b-2,c-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9'],
            'a-1,c-1':     ['e1', 'e2', 'e4', 'e6', 'e7', 'e8'],
            'a-1,b-2':     ['e1', 'e3', 'e4', 'e5', 'e7', 'e8', 'e9']
        }

        a = AlgorithmA('test6', f'{traces_dir_path}/trace_test6.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_7(self):
        expected_result = {
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

        a = AlgorithmA('test7', f'{traces_dir_path}/trace_test7.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_8(self):
        expected_result = {
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

        a = AlgorithmA('test8', f'{traces_dir_path}/trace_test8.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_9(self):
        expected_result = {
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

        a = AlgorithmA('test9', f'{traces_dir_path}/trace_test9.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_10(self):
        expected_result = {
            '':        ['e1', 'e10'],
            'a-1':     ['e1', 'e2', 'e9', 'e10'],
            'b-1':     ['e1', 'e3', 'e6', 'e10'],
            'a-1,b-1': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e9', 'e10'],
            'a-1,b-2': ['e1', 'e2', 'e7', 'e8', 'e9', 'e10'],
            'b-2':     ['e1', 'e7', 'e10']
        }

        a = AlgorithmA('test10', f'{traces_dir_path}/trace_test10.txt')
        current_state = a.algorithm_a(True)
        assert current_state == expected_result

    def test_case_11(self):
        expected_result = {
            '': [],
            "a-1": ['e1'],
            "a-1,b-1": ['e1', 'e2', 'e2']
        }

        a = AlgorithmA('test11', f'{traces_dir_path}/trace_test14.txt')
        current_state = a.algorithm_a(True)

        assert sorted(current_state) == sorted(expected_result)
