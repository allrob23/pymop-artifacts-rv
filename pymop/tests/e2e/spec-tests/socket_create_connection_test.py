import socket
import socketserver

# Define the host and port to connect to
host = 'www.google.com'
port = 80

def test_ok_1():
    assert 1 == 1

def test_ok_2():
    socket.create_connection((host, port), None)

def test_ok_3():
    socket.create_connection((host, port), 0)

def test_ok_4():
    socket.create_connection((host, port), 2.4)

def test_not_ok_1():
    socket.create_connection((host, port), -3)

def test_not_ok_2():
    socket.create_connection((host, port), -3.4)


expected_violations_A = 2
expected_violations_B = [test_not_ok_1, test_not_ok_2]
expected_violations_C = [test_not_ok_1, test_not_ok_2]
expected_violations_C_plus = [test_not_ok_1, test_not_ok_2]
expected_violations_D = [test_not_ok_1, test_not_ok_2]
