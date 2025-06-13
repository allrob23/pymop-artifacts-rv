from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    time.sleep(n)
    print(f"Task {n} completed")


def test_ok_1():
    thread_executor = ThreadPoolExecutor(max_workers=3)

    for i in range(5):
        thread_executor.submit(task, i)
    
    thread_executor.shutdown()


def test_ok_2():
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(5):
            executor.submit(task, i)


def test_violation_1():
    ThreadPoolExecutor(max_workers=3)


# All violations are marked test_violation_1 because this spec depends on the End event.
expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
