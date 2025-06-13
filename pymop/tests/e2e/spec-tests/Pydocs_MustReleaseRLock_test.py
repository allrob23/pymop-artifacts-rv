import threading
import time
import pytest


ok_lock = threading.RLock()
lock_to_acquire_and_release_but_not_enough_times = threading.RLock()
deadlocked_lock = threading.RLock()

def acquire_and_release_lock():
    ok_lock.acquire()

    # Wait a moment to demonstrate lock usage
    time.sleep(1)
    
    # Release the lock
    ok_lock.release()

    # try acquiring the lock again
    ok_lock.acquire()
    ok_lock.release()

# Client that tries to acquire the lock without releasing it
def access_without_releasing_lock():
    deadlocked_lock.acquire()
    
    # Intentionally not releasing the lock
    # We’ll let this lock go out of scope without releasing
    # This will cause every other thread depending on this lock to deadlock

def acquire_and_release_but_not_enough_times():
    lock_to_acquire_and_release_but_not_enough_times.acquire()
    lock_to_acquire_and_release_but_not_enough_times.acquire()

    # Wait a moment to demonstrate lock usage
    time.sleep(1)
    
    lock_to_acquire_and_release_but_not_enough_times.release()

def test_ok_1():
    thread_1 = threading.Thread(target=acquire_and_release_lock, daemon=True)
    thread_1.start()
    thread_1.join()

def test_ok_2():
    thread_1 = threading.Thread(target=acquire_and_release_lock, daemon=True)
    thread_2 = threading.Thread(target=acquire_and_release_lock, daemon=True)
    thread_3 = threading.Thread(target=acquire_and_release_lock, daemon=True)
    thread_4 = threading.Thread(target=acquire_and_release_lock, daemon=True)
    thread_1.start()
    thread_2.start()
    thread_3.start()
    thread_4.start()
    thread_1.join()
    thread_2.join()
    thread_3.join()
    thread_4.join()


def test_violation_1():
    thread_1 = threading.Thread(target=access_without_releasing_lock, daemon=True)
    # thread_2 = threading.Thread(target=access_without_releasing_lock, daemon=True) # this is deadlocked with thread_1
    thread_1.start()
    # thread_2.start()
    thread_1.join()
    # thread_2.join()

def test_violation_2():
    thread_1 = threading.Thread(target=acquire_and_release_but_not_enough_times, daemon=True)
    # thread_2 = threading.Thread(target=acquire_and_release_but_not_enough_times, daemon=True) # this is deadlocked with thread_1
    thread_1.start()
    # thread_2.start()
    thread_1.join()
    # thread_2.join()

# It's the same violaton 7 times; I think because we have 7 threads in total?! UPDATE: I think this comment is outdated
expected_violations_A = 2
expected_violations_B = [test_violation_2, test_violation_2]
expected_violations_C = [test_violation_2, test_violation_2]
expected_violations_C_plus = [test_violation_2, test_violation_2]
expected_violations_D = [test_violation_2, test_violation_2]
