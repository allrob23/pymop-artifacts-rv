from array import array

def test_ok_1():
    array_1 = array('i', [1])
    iter_1 = iter(array_1)
    next(iter_1)

def test_ok_2():
    array_1 = array('i')
    array_1.append(1)
    array_1.append(2)

    iter_1 = iter(array_1)
    next(iter_1)

def test_ok_3():
    array_1 = array('i')
    array_1.append(1)
    array_1.append(2)

    iter_1 = iter(array_1)
    next(iter_1)
    next(iter_1)

def test_ok_4():
    array_1 = array('i', [2])
    array_1.pop()
    array_1.append(4)

    iter_1 = iter(array_1)
    next(iter_1)

def test_ok_5():
    array_1 = array('i', [2])

    iter_1 = iter(array_1)
    next(iter_1)

    array_1.pop()
    array_1.append(4)

    iter_2 = iter(array_1)
    next(iter_2)

def test_ok_6():
    array_1 = array('i', [2])
    array_2 = array('i', [2])

    iter_1 = iter(array_1)

    array_2.pop()
    array_2.append(4)

    next(iter_1)

    iter_2 = iter(array_2)

    array_1.pop()
    array_1.append(4)

    next(iter_2)

def test_violation_1():
    array_1 = array('i')
    array_2 = array('i')

    array_1.append(99)
    array_2.append(99)

    iter_1 = iter(array_1)
    iter_2 = iter(array_2)

    # modified between iter creation and iter access
    array_1[0] = 1

    next(iter_2) # should show no violation because array_2 was not modified
    next(iter_1) # should show a violation since array_1 was modified

def test_violation_2():
    array_1 = array('i', [1, 2])

    iter_1 = iter(array_1)
    next(iter_1)

    array_1[0] = 1
    array_1[1] = 2

    next(iter_1)

    array_1.append(3)
    iter_2 = iter(array_1)

    array_1[1] = 1
    array_1[0] = 2

    next(iter_2)
    next(iter_2)
    next(iter_2)


def test_violation_3():
    array_1 = array('i', [1, 2, 3])
    iter_1 = iter(array_1)
    next(iter_1)
    
    array_1.append(4)  # Modification by appending
    
    next(iter_1)  # Should show a violation

def test_violation_4():
    array_1 = array('i', [1, 2, 3])
    iter_1 = iter(array_1)
    next(iter_1)
    
    array_1.pop()  # Modification by popping
    
    next(iter_1)  # Should show a violation

def test_violation_5():
    array_1 = array('i', [1, 2, 3])
    iter_1 = iter(array_1)
    next(iter_1)
    
    array_1.insert(1, 4)  # Modification by inserting
    
    next(iter_1)  # Should show a violation

def test_violation_6():
    array_1 = array('i', [1, 2, 3])
    iter_1 = iter(array_1)
    next(iter_1)
    
    array_1.extend([4, 5])  # Modification by extending
    
    next(iter_1)  # Should show a violation

def test_violation_7():
    array_1 = array('i', [1, 2, 3])
    iter_1 = iter(array_1)
    next(iter_1)
    
    array_1.remove(2)  # Modification by removing an element
    
    next(iter_1)  # Should show a violation

expected_violations_A = 8
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7]
