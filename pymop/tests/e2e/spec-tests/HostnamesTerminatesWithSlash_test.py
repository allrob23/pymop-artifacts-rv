from requests import Session

s = Session()

def test_ok_1():
    s.mount('https://youtube.com/', None)

def test_violation_1():
    s.mount('https://github.com', None)

def test_violation_2():
    s.mount('https://google.com', None)


expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
