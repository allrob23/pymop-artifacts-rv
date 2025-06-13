

def test_ok_1():
    # exiting the block automatically closes the other file f
    with open("test2.txt", "w") as t1:
        # Any code that uses the resource
        t1.write("Hello, World!")
        pass

def test_ok_2():
    t = open("test.txt", "w")
    t.read()
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
expected_violations_B = [test_violation_2, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_C = [test_violation_2, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_C_plus = [test_violation_2, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]
expected_violations_D = [test_violation_2, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4, test_violation_4]

# Algorithm A can show more violations than other algorithms because it replays events
# instead of copying the most informative params and then appending the new event.
# for instance, given the following trace:
#
# <event>: <params>
# ---------------------
# open: File-1
# close: File-1
# end: End-1
# ---------------------
#
# Algorithm A will process as follows:
# ------------------------------------------------------------------------------------------------------------------------------------
# - create a new parameter combination of (<File-1>)
# - add the event <open> to fsm of parameter combination (<File-1>)
# - add the event <close> to fsm of parameter combination (<File-1>)     <------------- The first violation is found here
# - create new parameter combinations of (<End-1>) and (<End-1>, <File-1>)
#
# - replay the events of the most informative parameter combination (<File-1>) to the new parameter combination of (<End-1>, <File-1>)
#     - replaying <open> to (<End-1>, <File-1>)
#     - replaying <close> to (<End-1>, <File-1>)   <------------- The second violation is found here
#
# - append the new event <end> to the new parameter combination of (<End-1>, <File-1>)
# ------------------------------------------------------------------------------------------------------------------------------------
#
# Other algorithms do not replay events, they only copy the current state of the most informative parameter combination.
# then when appending the new event <end>, no violation is found because it doesn't match the formalism.
expected_violations_A = 9
