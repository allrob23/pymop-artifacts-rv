import random

def test_ok_1():
    pass
    # Commented out as this would instrument random class which result the violation test from broken
    # random.seed(1, 10)
    # random.randint(1, 10)

def test_violation_1():
    random.randint(1, 10)

def test_violation_2():
    random.randint(1, 10)
    random.seed(1)
    random.randint(1, 10)

expected_violations_A = 4
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_2]
