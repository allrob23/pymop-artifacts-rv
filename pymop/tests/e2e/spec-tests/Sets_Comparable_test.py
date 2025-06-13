def test_ok_1():
    string_set = {"banana", "apple", "cherry"}
    sorted_set = sorted(string_set)

def test_ok_2():
    mixed_set = {3, "banana", 1, "apple"}
    sorted_set = sorted(mixed_set, key=str)

def test_ok_3():
    string_set = {"banana", "apple", "cherry"}
    sorted_set = sorted(string_set, key=len)

def test_violation_1():
	mixed_set = {3, "banana", 1, "apple"}

	try:
		# This will raise a TypeError because integers and strings cannot be compared
		sorted_set = sorted(mixed_set)
	except TypeError as e:
		pass

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
