def test_ok_1():
    string_list = ["banana", "apple", "cherry"]
    sorted_list = sorted(string_list)

def test_ok_2():
    mixed_list = [3, "banana", 1, "apple"]
    sorted_list = sorted(mixed_list, key=str)

def test_ok_3():
    string_list = ["banana", "apple", "cherry"]
    sorted_list = sorted(string_list, key=len)

def test_violation_1():
	mixed_list = [3, "banana", 1, "apple"]

	try:
		# This will raise a TypeError because integers and strings cannot be compared
		sorted_list = sorted(mixed_list)
	except TypeError as e:
		pass

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
