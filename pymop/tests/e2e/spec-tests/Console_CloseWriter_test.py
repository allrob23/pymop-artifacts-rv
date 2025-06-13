import sys
import io

def test_ok_1():
    assert 1 == 1

def test_violation_1():
    old_stdout = sys.stdout
    # flush sys.stdout
    sys.stdout.flush()

    # close sys.stdout
    sys.stdout.close()

    # reopen sys.stdout to prevent program from crashing
    sys.stdout = io.TextIOWrapper(io.FileIO(1, 'w'), write_through=True)

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
