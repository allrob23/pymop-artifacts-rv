import random

def test_ok_1():
    random.lognormvariate(0, 1)

def test_ok_2():
    random.vonmisesvariate(0, 0)

def test_ok_3():
    random.vonmisesvariate(0, 1)

def test_violation_1():
    random.lognormvariate(0, 0)

def test_violation_2():
    random.lognormvariate(0, -1)

def test_violation_3():
    random.vonmisesvariate(0, -1)

expected_violations_A = 3
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3]
