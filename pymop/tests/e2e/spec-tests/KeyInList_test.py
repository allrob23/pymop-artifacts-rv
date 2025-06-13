
def test_ok_1():
    set_1 = set([1, 2, 3, 4])
    1 in set_1

def test_violation_1():
    list_1 = list([1, 2, 3, 4])
    1 in list_1

def test_violation_2():
    list_2 = [1, 2, 3, 4]
    1 in list_2 # Doesn't work yet!

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
