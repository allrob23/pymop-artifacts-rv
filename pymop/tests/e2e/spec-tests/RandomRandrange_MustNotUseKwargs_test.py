import random

def test_ok_1():
    random.randrange(10)

def test_violation_1():
    random.randrange(10, 100, step=2)

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
