import requests


def test_violation_1():
    try:
        s = requests.Session()
        s.verify = '/tmp'
        s.get('https://github.com')
    except:
        pass


expected_violations_A = 6
expected_violations_B = [test_violation_1, test_violation_1, test_violation_1,
                         test_violation_1, test_violation_1, test_violation_1]
expected_violations_C = [test_violation_1, test_violation_1, test_violation_1,
                         test_violation_1, test_violation_1, test_violation_1]
expected_violations_C_plus = [test_violation_1, test_violation_1, test_violation_1,
                              test_violation_1, test_violation_1, test_violation_1]
expected_violations_D = [test_violation_1, test_violation_1, test_violation_1,
                         test_violation_1, test_violation_1, test_violation_1]
