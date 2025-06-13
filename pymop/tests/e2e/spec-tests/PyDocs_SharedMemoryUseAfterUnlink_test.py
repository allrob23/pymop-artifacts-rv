from multiprocessing import shared_memory, Process

def worker_read(shm_name):
    """Worker process to read data from shared memory."""
    shm = shared_memory.SharedMemory(name=shm_name)
    data = bytes(shm.buf[:]).decode()
    shm.close()
    return data

def worker_write(shm_name):
    """Worker process to write data to shared memory."""
    shm = shared_memory.SharedMemory(name=shm_name)

    shm.__getattribute__('buf')

    shm.buf[:5] = b"HELLO"
    shm.close()

def test_correct_usage_unlink():
    """Test the correct usage of unlink()."""
    # Create shared memory block
    shm = shared_memory.SharedMemory(create=True, size=1024)
    shm.buf[:5] = b"HELLO"  # Write some data

    # Spawn a process to read from the shared memory
    process = Process(target=worker_read, args=(shm.name,))
    process.start()
    process.join()

    # Close and unlink the shared memory
    shm.close()
    shm.unlink()  # Proper cleanup

def test_incorrect_usage_read_after_unlink():
    """Test incorrect usage: reading shared memory after unlink()."""
    shm = shared_memory.SharedMemory(create=True, size=1024)
    shm.buf[:5] = b"HELLO"

    shm2 = shared_memory.SharedMemory(name=shm.name)
    shm.unlink()

    data = bytes(shm2.buf[:]).decode() # <-------------------------- VIOLATION
    data = bytes(shm.buf[:]).decode() # <--------------------------- VIOLATION

def test_incorrect_usage_access_after_unlink():
    """Test incorrect usage: accessing shared memory after unlink()."""
    shm = shared_memory.SharedMemory(create=True, size=1024)
    shm.buf[:5] = b"HELLO"

    # Unlink the shared memory
    shm.unlink()

    # Attempt to access the memory block after unlinking
    shm.buf[:5] = b"WORLD" # <--------------------------- VIOLATION

    shm.close()


expected_violations_A = 3
expected_violations_B = [test_incorrect_usage_read_after_unlink, test_incorrect_usage_read_after_unlink, test_incorrect_usage_access_after_unlink]
expected_violations_C = [test_incorrect_usage_read_after_unlink, test_incorrect_usage_read_after_unlink, test_incorrect_usage_access_after_unlink]
expected_violations_C_plus = [test_incorrect_usage_read_after_unlink, test_incorrect_usage_read_after_unlink, test_incorrect_usage_access_after_unlink]
expected_violations_D = [test_incorrect_usage_read_after_unlink, test_incorrect_usage_read_after_unlink, test_incorrect_usage_access_after_unlink]
