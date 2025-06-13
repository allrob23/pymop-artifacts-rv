import mmap
import os
import pytest

file_path = 'sample.txt'

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: Create a sample file to be memory-mapped
    with open(file_path, 'wb') as f:
        f.write(b'Hello, world!')
    yield
    # Teardown: Clean up the sample file
    os.remove(file_path)

def test_modify_and_flush():
    # Open the file and create a memory-mapped object
    with open(file_path, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)

        # Modify the content via mmap
        mm[0:5] = b'Hi!!!'

        # Ensure changes are written to the underlying file
        mm.flush()

        # Close the mmap object
        mm.close()

def test_modify_without_flush():
    # Open the file and create a memory-mapped object
    with open(file_path, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)

        # Modify the content via mmap
        mm[0:13] = b'Hi???, world?'

        # mm.flush() # <---------------------- VIOLATION here because the flush is not called

        # Close the mmap object without flushing
        mm.close()

expected_violations_A = 1
expected_violations_B = [test_modify_without_flush]
expected_violations_C = [test_modify_without_flush]
expected_violations_C_plus = [test_modify_without_flush]
expected_violations_D = [test_modify_without_flush]
