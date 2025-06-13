import sys
import pytest
import io


def test_ok_1():
    assert 1 == 1


def test_violation_1():
    sys.stderr.flush()
    sys.stderr.close()
    # reopen stderr to prevent program from crash
    sys.stderr = io.TextIOWrapper(io.FileIO(2, 'w'), write_through=True)


expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]

