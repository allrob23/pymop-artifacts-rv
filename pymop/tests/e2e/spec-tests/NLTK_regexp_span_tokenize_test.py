from nltk.tokenize.util import regexp_span_tokenize

def test_ok_1():
    assert True == True, "Should be true"

def test_ok_2():
    s = "Good muffins cost $3.88 in New York. Please buy me two of them. Thanks."
    regexp_span_tokenize(s, 's')

def test_violation_1():
    s = "Good muffins cost $3.88 in New York. Please buy me two of them. Thanks."
    regexp_span_tokenize(s, '')

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
