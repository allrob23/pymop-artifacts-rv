from requests import Session


with open('test.txt', 'w') as f:
    f.write('test')

def test_ok_1():
    with open('test.txt', 'rb') as f:
        session = Session()
        s = session.post('https://github.com/', data=f)

def test_violation_1():
    with open('test.txt', 'r') as f:
        session = Session()
        s = session.post('https://github.com/', data=f)

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
