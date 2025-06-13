from nltk.tokenize import RegexpTokenizer


def test_ok_1():
    assert True == True, "Should be true"


def test_ok_2():
    RegexpTokenizer(r'(?:\w+)|(?:[^\w\s]+)')


def test_violation_1():
    RegexpTokenizer(r'(\w+)|([^\w\s]+)')


expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
