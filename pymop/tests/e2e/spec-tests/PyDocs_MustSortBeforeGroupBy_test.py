import builtins
import itertools

def test_ok_1():
    my_list = builtins.list([12, 32])
    my_list.sort()
    itertools.groupby(my_list)

def test_ok_2():
    my_list = builtins.list([12, 32])
    my_list.sort()

    my_list.append(1)

    my_list.remove(12)

    my_list.sort()

    itertools.groupby(my_list)

# This does not work for now because of a bug in PythonMop. Enable it when the bug is fixed.
# def test_ok_3():
#     my_list = builtins.list([12, 32])
#     sorted(my_list)
#     itertools.groupby(my_list)

def test_ok_3():
    my_list = builtins.list([12, 32])
    my_list.sort()
    my_list.extend([1, 2])
    my_list.sort()
    itertools.groupby(my_list)

def test_violation_1():
    my_list = builtins.list([12, 32])
    itertools.groupby(my_list)

def test_violation_2():
    my_list = builtins.list([12, 32])
    my_list.sort()

    my_list.append(1)
    itertools.groupby(my_list)

def test_violation_3():
    my_list = builtins.list([12, 32])
    my_list.sort()
    my_list.remove(12)
    itertools.groupby(my_list)

def test_violation_4():
    my_list = builtins.list([12, 32])
    my_list.sort()
    my_list.pop(0)
    itertools.groupby(my_list)

def test_violation_5():
    my_list = builtins.list([12, 32])
    my_list.sort()
    my_list.insert(0, 1)
    itertools.groupby(my_list)

def test_violation_6():
    my_list = builtins.list([12, 32])
    my_list.sort()
    my_list.extend([1, 2])
    itertools.groupby(my_list)

def test_violation_7():
    my_list = [12, 32]
    my_list.sort()
    my_list.extend([1, 2])
    itertools.groupby(my_list)

expected_violations_A = 7
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
