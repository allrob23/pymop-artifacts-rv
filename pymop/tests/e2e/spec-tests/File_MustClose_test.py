

def test_ok_1():
    # exiting the block automatically closes the other file f
    with open("test2.txt", "w") as t1:
        # Any code that uses the resource
        pass

def test_ok_2():
    t = open("test.txt", "w")
    t.close()    

def test_violation_1():
    # forgot to close the file t
    t = open("test.txt", "w")

def test_violation_2():
    t1 = open('test.test', 'w')
    t2 = open('test2.test', 'w')
    t1.close()

def test_violation_3():
    t1 = open('test.test', 'w')
    t2 = open('test2.test', 'w')

def test_violation_4():
    with open("test2.txt", "w") as t1:
        # Any code that uses the resource
        t2 = open('test.test', 'w')


# this spec uses the hook End, so it will show the violation after all the tests have run.
expected_violations_A = 5
expected_violations_B = [test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_C = [test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_C_plus = [test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_D = [test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
