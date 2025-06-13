import threading
import time
import pytest

def blocking_acquire_and_releasing_lock(lock, wait):
    lock.acquire()

    # Wait a moment to demonstrate lock usage
    wait.acquire()
    wait.release()
    
    # Release the lock
    lock.release()

    # try acquiring the lock again
    lock.acquire()
    lock.release()

# Client that tries to acquire the lock without releasing it
def blocking_acquire_without_releasing_lock(lock):
    lock.acquire()
    
    # Intentionally not releasing the lock
    # We’ll let this lock go out of scope without releasing
    # This will cause every other thread depending on this lock to deadlock

def nonblocking_acquire_lock_without_releasing_lock(lock):
    lock.acquire(False)

def nonblocking_acquire_lock_and_release_lock(lock):
    lock.acquire(False)
    lock.release()

def test_ok_1():
    lock = threading.Lock()
    thread_1 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, threading.Lock()))
    thread_1.start()
    thread_1.join()

def test_ok_2():
    lock = threading.Lock()
    thread_1 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, threading.Lock()))
    thread_2 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, threading.Lock()))
    thread_3 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, threading.Lock()))
    thread_4 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, threading.Lock()))
    thread_1.start()
    thread_2.start()
    thread_3.start()
    thread_4.start()
    thread_1.join()
    thread_2.join()
    thread_3.join()
    thread_4.join()

def test_ok_3():
    # This test will show a warning that a lock is being released while it wasn't acquired, but it's ok
    lock = threading.Lock()
    wait = threading.Lock()
    wait.acquire()

    thread_1 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, wait))
    thread_2 = threading.Thread(target=nonblocking_acquire_lock_and_release_lock, daemon=True, args=(lock,))

    thread_1.start()

    thread_2.start()
    thread_2.join()

    wait.release()
    thread_1.join()

def test_ok_4():
    lock = threading.Lock()
    lock.acquire()
    thread_2 = threading.Thread(target=nonblocking_acquire_lock_without_releasing_lock, daemon=True, args=(lock,))
    thread_2.start()
    thread_2.join()
    lock.release()

def test_ok_5():
    lock = threading.Lock()
    with lock:
        pass

def test_ok_6():
    lock = threading.Lock()
    wait = threading.Lock()
    wait.acquire()
    thread_1 = threading.Thread(target=blocking_acquire_without_releasing_lock, daemon=True, args=(lock,)) # this will acquire the lock
    thread_2 = threading.Thread(target=nonblocking_acquire_lock_and_release_lock, daemon=True, args=(lock,)) # this will try to acquire and fail, but release it anyways
    thread_3 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, wait)) # this will succeed to acquire the lock because it was freed by thread_2

    thread_1.start()
    thread_1.join() # make sure thread_1 is done before thread_2 starts

    thread_2.start()
    thread_2.join() # make sure thread_2 is done before thead_3 starts

    wait.release()
    thread_3.start()
    thread_3.join()

def test_ok_7():
    lock = threading.Lock()
    thread_1 = threading.Thread(target=nonblocking_acquire_lock_without_releasing_lock, daemon=True, args=(lock,)) # this will acquire the lock
    thread_2 = threading.Thread(target=nonblocking_acquire_lock_and_release_lock, daemon=True, args=(lock,)) # this will try to acquire and fail, but release it anyways

    thread_1.start()
    thread_1.join() # make sure thread_1 is done before thread_2 starts

    thread_2.start()
    thread_2.join()

def test_violation_1():
    lock = threading.Lock()
    thread_1 = threading.Thread(target=blocking_acquire_without_releasing_lock, daemon=True, args=(lock,))
    thread_1.start()
    thread_1.join()

def test_violation_2():
    lock = threading.Lock()
    thread_1 = threading.Thread(target=nonblocking_acquire_lock_without_releasing_lock, daemon=True, args=(lock,))
    thread_2 = threading.Thread(target=nonblocking_acquire_lock_without_releasing_lock, daemon=True, args=(lock,))
    thread_1.start()
    thread_1.join()
    thread_2.start()
    thread_2.join()

def test_violation_3():
    lock = threading.Lock()
    wait = threading.Lock()
    thread_1 = threading.Thread(target=nonblocking_acquire_lock_without_releasing_lock, daemon=True, args=(lock,))
    thread_2 = threading.Thread(target=blocking_acquire_and_releasing_lock, daemon=True, args=(lock, wait)) # this will be blocked by thread_1
    thread_1.start()
    thread_1.join()
    thread_2.start()
    thread_2.join(5)

# All violations show as violation_3 because this spec depends on End event
expected_violations_A = 3
expected_violations_B = [test_violation_3, test_violation_3, test_violation_3]
expected_violations_C = [test_violation_3, test_violation_3, test_violation_3]
expected_violations_C_plus = [test_violation_3, test_violation_3, test_violation_3]
expected_violations_D = [test_violation_3, test_violation_3,test_violation_3]
