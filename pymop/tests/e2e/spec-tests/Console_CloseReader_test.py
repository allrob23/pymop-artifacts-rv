import sys
import pytest

def test_ok_1():
    assert 1 == 1


def test_violation_1():
    sys.stdin.close()

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
