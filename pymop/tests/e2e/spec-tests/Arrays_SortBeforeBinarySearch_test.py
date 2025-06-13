import pytest
import bisect

def test_ok_1():
    my_list = [2, 3, 1]
    my_list = sorted(my_list)
    my_list = sorted(my_list)
    bisect.bisect_right(my_list, 1)

def test_ok_2():
    my_list = [2, 3, 1]
    my_list = sorted(my_list)
    bisect.bisect_left(my_list, 1)
    bisect.bisect_right(my_list, 1)

def test_ok_3():
    my_list = [2, 3, 1]

    my_list = sorted(my_list)
    my_list.append(9)
    my_list = sorted(my_list)

    bisect.bisect_left(my_list, 1)

def test_ok_4():
    my_list = [2, 3, 1]
    my_list.append(9)
    
    my_list = sorted(my_list)

    bisect.bisect_right(my_list, 1)

def test_ok_5():
    my_list = list([1, 2, 3])
    my_list.sort()

    bisect.bisect_right(my_list, 1)

def test_ok_6():
    my_list = list([2, 4, 5])

    my_list_2 = sorted(my_list)

    my_list.sort()

    bisect.bisect_right(my_list, 1)
    bisect.bisect_right(my_list_2, 1)

# this test case is not supported yet since we
# can't listen to list literal events
# def test_ok_7():
#     my_list = [1, 2, 3]
#     my_list.sort()
    
#     bisect.bisect_left(my_list, 1)

def test_violation_1():
    my_list = [2, 3, 1]
    bisect.bisect_right(my_list, 1)

def test_violation_2():
    my_list = [2, 3, 1]
    bisect.bisect_left(my_list, 1)
    bisect.bisect_right(my_list, 1)

def test_violation_3():
    my_list = [2, 3, 1]
    my_list.append(9)
    bisect.bisect_left(my_list, 1)

def test_violation_4():
    my_list = list([2, 3, 1])
    my_list = sorted(my_list)
    my_list.append(9)
    bisect.bisect_right(my_list, 1)

def test_violation_5():
    my_list = [2, 3, 1]
    my_list = sorted(my_list)
    my_list.append(9)
    bisect.bisect_right(my_list, 1)

def test_violation_6():
    my_list = [2, 3, 1]
    my_list.append(9)
    
    sorted(my_list) # did not re-assign my_list

    bisect.bisect_right(my_list, 1)


expected_violations_A = 7
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6]
