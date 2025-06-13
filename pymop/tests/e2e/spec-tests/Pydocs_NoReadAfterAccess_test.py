
import os

insensitive_filename = "insensitive_file.txt"

with open(insensitive_filename, "w") as f:
    f.write("This is some public info.")

def test_ok_1():
    with open(insensitive_filename) as f:
        f.read()

def test_ok_2():
    os.access(insensitive_filename, os.R_OK)

def test_violation_1():
    if os.access(insensitive_filename, os.R_OK):
        with open(insensitive_filename) as f:
            f.read()


expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
