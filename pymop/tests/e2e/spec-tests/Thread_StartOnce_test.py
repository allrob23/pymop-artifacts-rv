import pytest
import threading
import random

NUM_THREADS = 10


def run():
    pass


def test_ok_1():
    assert 1 == 1


def test_ok_2():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()


def test_ok_3():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    # start all threads
    for thread in threads:
        thread.start()


def test_violation_1():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()
    my_thread2.start()


def test_violation_2():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()
    try:
        my_thread2.start()
    except RuntimeError:
        pass


def test_violation_3():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    # start all threads
    for thread in threads:
        thread.start()
    threads[0].start()


def test_violation_4():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    # start all threads
    for thread in threads:
        thread.start()

    random.shuffle(threads)
    try:
        threads[0].start()
    except RuntimeError:
        pass


def test_ok_4():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread.join()


def test_ok_5():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread.join()


def test_ok_6():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

# Tests for violating the specification of "threads can only be started once"


def test_violation_5():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    with pytest.raises(RuntimeError):
        my_thread.start()


def test_violation_6():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()
    my_thread.join()
    my_thread2.start()


def test_violation_7():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    for thread in threads:
        thread.start()
    threads[0].join()
    threads[0].start()

# Tests for violating the specification with exhausted threads


def test_violation_8():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread.join()
    with pytest.raises(RuntimeError):
        my_thread.start()


def test_violation_9():
    my_thread = threading.Thread(target=run)
    my_thread.start()
    my_thread2 = threading.Thread(target=run)
    my_thread2.start()
    my_thread.join()
    with pytest.raises(RuntimeError):
        my_thread2.start()


def test_violation_10():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    with pytest.raises(RuntimeError):
        threads[0].start()

# Randomized tests for violating the specification


def test_violation_11():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    for thread in threads:
        thread.start()
    random.shuffle(threads)
    with pytest.raises(RuntimeError):
        threads[0].start()


def test_violation_12():
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=run))
    for thread in threads:
        thread.start()
    random.shuffle(threads)
    for thread in threads:
        thread.join()
    with pytest.raises(RuntimeError):
        threads[0].start()


def test_ok_7():
    def nested_thread():
        thread = threading.Thread(target=run)
        thread.start()

    main_thread = threading.Thread(target=nested_thread)
    main_thread.start()


def test_ok_8():
    thread1 = threading.Thread(target=run, name="thread1")
    thread2 = threading.Thread(target=run, name="thread1")
    thread1.start()
    thread2.start()


def test_ok_9():
    thread1 = threading.Thread(target=run, daemon=True)
    thread2 = threading.Thread(target=run, daemon=False)
    thread3 = threading.Thread(target=run, daemon=False)
    thread1.start()
    thread2.start()
    thread3.start()


class CustomThread(threading.Thread):
    def run(self):
        pass


def test_ok_10():
    thread = CustomThread()
    thread.start()


def test_violation_13():
    thread = CustomThread()
    thread.start()
    try:
        thread.start()
    except RuntimeError:
        pass


def test_violation_14():
    thread = threading.Thread(target=run)
    try:
        a = 10
        thread.start()
    finally:
        thread.start()


def test_violation_15():
    thread = threading.Thread(target=run)
    thread.start()
    thread.join()
    thread.start()


def test_violation_16():
    with threading.Lock():
        thread = threading.Thread(target=run)
        thread.start()  # Should raise RuntimeError
        thread.start()


expected_violations_A = 16
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8, test_violation_9, test_violation_10, test_violation_11, test_violation_12, test_violation_13, test_violation_14, test_violation_15, test_violation_16]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8, test_violation_9, test_violation_10, test_violation_11, test_violation_12, test_violation_13, test_violation_14, test_violation_15, test_violation_16]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8, test_violation_9, test_violation_10, test_violation_11, test_violation_12, test_violation_13, test_violation_14, test_violation_15, test_violation_16]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5, test_violation_6, test_violation_7, test_violation_8, test_violation_9, test_violation_10, test_violation_11, test_violation_12, test_violation_13, test_violation_14, test_violation_15, test_violation_16]
