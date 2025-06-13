def test_ok_1():
    map_1 = dict({1: 1})
    iter_1 = iter(map_1)
    next(iter_1)

def test_ok_2():
    map_1 = dict()
    map_1[1] = 1
    map_1[1] = 2

    iter_1 = iter(map_1)
    next(iter_1)

def test_ok_3():
    map_1 = dict()
    map_1[1] = 1
    map_1[2] = 2

    iter_1 = iter(map_1)
    next(iter_1)
    next(iter_1)

def test_ok_4():
    map_1 = dict({2: 2})
    del map_1[2]
    map_1[3] = 4

    iter_1 = iter(map_1)

    next(iter_1)

def test_ok_5():
    map_1 = dict({2: 2})

    iter_1 = iter(map_1)
    next(iter_1)

    del map_1[2]
    map_1[3] = 4

    iter_2 = iter(map_1)
    next(iter_2)

def test_ok_6():
    map_1 = dict({2: 2})
    map_2 = dict({2: 2})

    iter_1 = iter(map_1)

    del map_2[2]
    map_2[3] = 4

    next(iter_1)

    iter_2 = iter(map_2)

    del map_1[2]
    map_1[3] = 4

    next(iter_2)

def test_violation_1():
    map_1 = dict()
    map_2 = dict()

    map_1[1] = 99
    map_2[1] = 99

    iter_1 = iter(map_1)
    iter_2 = iter(map_2)

    # modified between iter creation and iter access
    map_1[1] = 1

    next(iter_2) # should show no violation because map_2 was not modified
    next(iter_1) # should show a violation since map_1 was modified

def test_violation_2():
    map_1 = dict({1: 1, 2: 2})

    iter_1 = iter(map_1)
    next(iter_1)

    map_1[1] = 1
    map_1[2] = 2

    next(iter_1)

    map_1[3] = 3
    iter_2 = iter(map_1)

    map_1[2] = 1
    map_1[1] = 2

    next(iter_2)
    next(iter_2)
    next(iter_2)


def test_violation_3():
    # Test violation with dict.update()
    map_1 = dict({1: 1, 2: 2})
    iter_1 = iter(map_1)
    next(iter_1)
    
    map_1.update({1: 3, 2: 4}) 
    
    next(iter_1)  # should show a violation

def test_violation_4():
    # Test violation with dict.pop()
    map_1 = dict({1: 1, 2: 2, 3: 3})
    iter_1 = iter(map_1)
    next(iter_1)
    
    map_1.pop(2)  # Removing a key
    
    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_5():
    # Test violation with dict.popitem()
    map_1 = dict({1: 1, 2: 2, 3: 3})
    iter_1 = iter(map_1)
    next(iter_1)
    
    map_1.popitem()  # Removing the last inserted item
    
    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_6():
    # Test violation with dict.clear()
    map_1 = dict({1: 1, 2: 2, 3: 3})
    iter_1 = iter(map_1)
    next(iter_1)
    
    map_1.clear()  # Removing all items

    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_7():
    # Test violation with dict.setdefault() adding new key
    map_1 = dict({1: 1, 2: 2})
    iter_1 = iter(map_1)
    next(iter_1)
    
    map_1.setdefault(3, 3)  # This will add a new key-value pair
    
    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_8():
    # Test violation with del
    map_1 = dict({1: 1, 2: 2, 3: 3})
    iter_1 = iter(map_1)
    next(iter_1)
    
    del map_1[2]  # Removing a key
    
    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_9():
    # Test violation with del
    map_1 = {1: 1, 2: 2, 3: 3}
    iter_1 = iter(map_1)
    next(iter_1)
    
    del map_1[2]  # Removing a key
    
    # may fail because dict size has changed, but that's fine
    next(iter_1)  # should show a violation

def test_violation_10():
    '''
    !! Not yet supported !!
    '''
    a = {'x': 1}
    b = {'y': 2}
    c = {'x': 99, 'z': 3}
    merged = {**a, **b, 'x': 100, **c}

    iter_1 = iter(merged)
    next(iter_1)

def test_violation_20():
    def foo(list):
        for i in list:
            print(i)

    list = [1, 2, 3]
    foo(list)

def test_violation_21():
    def foo(list):
        for i in list:
            print(i)

    class A(): pass

    list = A
list()

expected_violations_A = 9
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8]
