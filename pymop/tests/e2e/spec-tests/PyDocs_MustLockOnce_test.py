import threading
import time
import unittest

class TestLockUsage(unittest.TestCase):
    def setUp(self):
        self.lock = threading.Lock()
        self.thread_result = None
        self.thread_exception = None

    def run_in_thread(self, target):
        """Helper to run a function in a thread and capture its result/exception"""
        def wrapper():
            try:
                self.thread_result = target()
            except Exception as e:
                self.thread_exception = e
        
        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        thread.join(timeout=1.0)  # 1 second timeout
        return thread.is_alive()  # True if thread is still running (deadlocked)

    def test_correct_lock_usage(self):
        """Test correct usage of lock acquire/release"""
        def target():
            self.lock.acquire()
            time.sleep(0.1)  # Simulate some work
            self.lock.release()
            return True

        is_deadlocked = self.run_in_thread(target)
        self.assertFalse(is_deadlocked, "Thread should complete normally")
        self.assertTrue(self.thread_result, "Thread should return successfully")
        self.assertIsNone(self.thread_exception, "No exceptions should be raised")

    def test_double_acquire_deadlock(self):
        """Test that acquiring the same lock twice causes a deadlock"""
        def target():
            self.lock.acquire()
            time.sleep(0.1)  # Simulate some work
            self.lock.acquire()  # This should deadlock
            return True

        is_deadlocked = self.run_in_thread(target)
        self.assertTrue(is_deadlocked, "Thread should be deadlocked")

    def test_correct_with_statement(self):
        """Test correct usage with context manager"""
        def target():
            with self.lock:
                time.sleep(0.1)  # Simulate some work
            return True

        is_deadlocked = self.run_in_thread(target)
        self.assertFalse(is_deadlocked, "Thread should complete normally")
        self.assertTrue(self.thread_result, "Thread should return successfully")
        self.assertIsNone(self.thread_exception, "No exceptions should be raised")

    # TODO: Our spec currently does not detect this deadlock.
    # We need to fix it.
    def test_nested_with_statement_deadlock(self):
        """Test that nested with statements on the same lock cause a deadlock"""
        def target():
            with self.lock:
                with self.lock:  # This should deadlock
                    pass
            return True

        is_deadlocked = self.run_in_thread(target)
        self.assertTrue(is_deadlocked, "Thread should be deadlocked")

if __name__ == '__main__':
    unittest.main()



expected_violations_A = 1
expected_violations_B = [TestLockUsage.test_double_acquire_deadlock]
expected_violations_C = [TestLockUsage.test_double_acquire_deadlock]
expected_violations_C_plus = [TestLockUsage.test_double_acquire_deadlock]
expected_violations_D = [TestLockUsage.test_double_acquire_deadlock]
