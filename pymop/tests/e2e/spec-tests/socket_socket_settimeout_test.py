import socket

# create a new socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def test_ok_1():
    assert 1 == 1

def test_ok_2():
    s.settimeout(None)

def test_ok_3():
    s.settimeout(0)

def test_ok_4():
    s.settimeout(2.4)

def test_not_ok_1():
    s.settimeout(-3)

def test_not_ok_2():
    s.settimeout(-3.4)

expected_violations_A = 2
expected_violations_B = [test_not_ok_1, test_not_ok_2]
expected_violations_C = [test_not_ok_1, test_not_ok_2]
expected_violations_C_plus = [test_not_ok_1, test_not_ok_2]
expected_violations_D = [test_not_ok_1, test_not_ok_2]
