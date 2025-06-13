
import subprocess

def test_ok_1():
    p = subprocess.Popen('ls')
    p.wait()

def test_ok_2():
    p = subprocess.Popen('ls')
    p.communicate()

def test_ok_3():
    with subprocess.Popen('ls') as p:
        pass

def test_ok_4():
    p = subprocess.Popen('non-existing-command')
    p.wait()

def test_ok_5():
    with subprocess.Popen('non-existing-command') as p:
        pass

def test_violation_1():
    subprocess.Popen('ls')
    # p.wait() # <------------- VIOLATION: must wait for Popen to finish before exiting the program

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
