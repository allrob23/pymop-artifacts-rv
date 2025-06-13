def test_ok_1():
    list_1 = list([1])
    iter_1 = iter(list_1)
    next(iter_1)

def test_ok_2():
    list_1 = list()
    list_1.append(1)
    list_1.append(2)

    iter_1 = iter(list_1)
    next(iter_1)

def test_ok_3():
    list_1 = list()
    list_1.append(1)
    list_1.append(2)

    iter_1 = iter(list_1)
    next(iter_1)
    next(iter_1)

def test_ok_4():
    list_1 = list([2])
    list_1.pop()
    list_1.append(4)

    iter_1 = iter(list_1)
    next(iter_1)

def test_ok_5():
    list_1 = list([2])

    iter_1 = iter(list_1)
    next(iter_1)

    list_1.pop()
    list_1.append(4)

    iter_2 = iter(list_1)
    next(iter_2)

def test_ok_6():
    list_1 = list([2])
    list_2 = list([2])

    iter_1 = iter(list_1)

    list_2.pop()
    list_2.append(4)

    next(iter_1)

    iter_2 = iter(list_2)

    list_1.pop()
    list_1.append(4)

    next(iter_2)

def test_violation_1():
    list_1 = list()
    list_2 = list()

    list_1.append(99)
    list_2.append(99)

    iter_1 = iter(list_1)
    iter_2 = iter(list_2)

    # modified between iter creation and iter access
    list_1[0] = 1

    next(iter_2) # should show no violation because list_2 was not modified
    next(iter_1) # should show a violation since list_1 was modified

def test_violation_2():
    list_1 = list([1, 2])

    iter_1 = iter(list_1)
    next(iter_1)

    list_1[0] = 1
    list_1[1] = 2

    next(iter_1)

    list_1.append(3)
    iter_2 = iter(list_1)

    list_1[1] = 1
    list_1[0] = 2

    next(iter_2)
    next(iter_2)
    next(iter_2)


def test_violation_3():
    list_1 = list([1, 2, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.append(4)  # Modification by appending
    
    next(iter_1)  # Should show a violation

def test_violation_4():
    list_1 = list([1, 2, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.pop()  # Modification by popping
    
    next(iter_1)  # Should show a violation

def test_violation_5():
    list_1 = list([1, 2, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.insert(1, 4)  # Modification by inserting
    
    next(iter_1)  # Should show a violation

def test_violation_6():
    list_1 = list([1, 2, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.extend([4, 5])  # Modification by extending
    
    next(iter_1)  # Should show a violation

def test_violation_7():
    list_1 = list([1, 2, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.remove(2)  # Modification by removing an element
    
    next(iter_1)  # Should show a violation

def test_violation_8():
    list_1 = list([2, 1, 3])
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.sort()  # Modification by 
    
    next(iter_1)  # Should show a violation

def test_violation_9():
    list_1 = [2, 1, 3]
    iter_1 = iter(list_1)
    next(iter_1)
    
    list_1.sort()  # Modification by 
    
    next(iter_1)  # Should show a violation

expected_violations_A = 9
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]

