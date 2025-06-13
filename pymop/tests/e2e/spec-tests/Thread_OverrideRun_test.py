import threading


def run():
    pass


def test_ok_1():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()


def test_ok_2():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()
    my_thread2.join()


def test_ok_3():
    class MyThread(threading.Thread):
        def run(self):
            pass

    my_thread = MyThread()
    my_thread.start()


def test_violation_01():
    # creating a thread without changing the target
    my_thread = threading.Thread()
    my_thread.start()


def test_violation_02():
    # creating a thread without changing the target
    my_thread = threading.Thread()
    my_thread.start()
    my_thread.join()


def test_violation_03():
    # creating a thread without changing the target
    class MyViolationThread(threading.Thread):
        pass

    my_thread = MyViolationThread()
    my_thread.start()


expected_violations_A = 3
expected_violations_B = [test_violation_01, test_violation_02, test_violation_03]
expected_violations_C = [test_violation_01, test_violation_02, test_violation_03]
expected_violations_C_plus = [test_violation_01, test_violation_02, test_violation_03]
expected_violations_D = [test_violation_01, test_violation_02, test_violation_03]
