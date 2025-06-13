import requests


def test_ok_1():
    req = requests.Request('GET', 'http://httpbin.org/get')
    r = req.prepare()

    s = requests.Session()
    s.send(r)


def test_violation_1():
    # Manually creating a PreparedRequest object (not recommended)
    prep = requests.PreparedRequest()

    # Attempting to set URL and method manually
    prep.prepare_method('GET')
    prep.prepare_url('https://httpbin.org/get', None)

    # Since we haven't gone through the correct preparation steps,
    # sending this PreparedRequest might result in errors or unexpected behavior.
    try:
        s2 = requests.Session()
        s2.send(prep)
    except Exception as e:
        print(f"An error occurred: {e}")

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_1]
expected_violations_C = [test_violation_1, test_violation_1]
expected_violations_C_plus = [test_violation_1, test_violation_1]
expected_violations_D = [test_violation_1, test_violation_1]
