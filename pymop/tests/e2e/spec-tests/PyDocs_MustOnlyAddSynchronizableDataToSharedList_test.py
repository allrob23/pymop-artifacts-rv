import pytest
from multiprocessing import Manager

@pytest.fixture
def manager_and_list():
    """Fixture to provide a Manager.list for tests."""
    with Manager() as manager:
        yield (manager, manager.list())


def test_ok_1(manager_and_list):
    """Test appending a synchronizable object to Manager.list."""
    manager, shared_list = manager_and_list
    shared_list.append(42)
    assert shared_list[0] == 42


def test_ok_2(manager_and_list):
    """Test appending a synchronizable object to Manager.list."""
    manager, shared_list = manager_and_list

    # append a shared list
    new_shared_list = manager.list()
    shared_list.append(new_shared_list)


def test_ok_3(manager_and_list):
    """Test appending a synchronizable object to Manager.list."""
    manager, shared_list = manager_and_list
    shared_dict = manager.dict()
    shared_list.append(shared_dict)


def test_violation_1(manager_and_list):
    """Test appending a raw dict to Manager.list."""
    manager, shared_list = manager_and_list
    raw_dict = {"key": "value"}
    shared_list.append(raw_dict) # <----------------------- VIOLATION
    assert shared_list[0] is not raw_dict  # dict constructed on the other side, but it's not the same dict.


def test_violation_2(manager_and_list):
    """Test appending a raw list to Manager.list."""
    manager, shared_list = manager_and_list
    raw_list = [1, 2, 3]
    shared_list.append(raw_list) # <----------------------- VIOLATION
    assert shared_list[0] is not raw_list  # list constructed on the other side, but it's not the same list.


def test_violation_3(manager_and_list):
    """Test appending a socket object to Manager.list."""
    manager, shared_list = manager_and_list
    import socket
    s = socket.socket()
    shared_list.append(s) # <----------------------- VIOLATION
    assert shared_list[0] is not s  # Socket constructed on the other side, but it's not the same socket.
    s.close()


def test_violation_4(manager_and_list):
    """Test appending a shared memory object to Manager.list."""
    from multiprocessing.shared_memory import SharedMemory
    manager, shared_list = manager_and_list
    shm = SharedMemory(create=True, size=10)
    shared_list.append(shm) # <----------------------- VIOLATION
    assert shared_list[0] is not shm  # Shared memory constructed on the other side, but it's not the same shared memory.
    shm.close()


expected_violations_A = 4
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
