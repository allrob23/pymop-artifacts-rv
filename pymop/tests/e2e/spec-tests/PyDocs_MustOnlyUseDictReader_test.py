import os
import uuid
import csv
from io import StringIO

def test_ok_1():
    file_content = StringIO("name,age\nAlice,30\nBob,25\n")
    
    reader = csv.DictReader(file_content)
    
    row1 = next(reader)
    assert row1 == {'name': 'Alice', 'age': '30'}

    row2 = next(reader)
    assert row2 == {'name': 'Bob', 'age': '25'}


def test_ok_2():
    file_content = StringIO("name,age\nAlice,30\nBob,25\n")
    
    # Calling readline directly on the file before using DictReader
    first_line = file_content.readline()
    assert first_line == "name,age\n"  # First line read directly
    
    reader = csv.DictReader(file_content)
    
    row1 = next(reader)

    # Results look weird because DictReader is using the second line as the header.
    # this is ok for this spec, we can monitor this behavior in a different spec.
    assert row1 == {'30': '25', 'Alice': 'Bob'}

def test_ok_3():
    file_content = StringIO("name,age\nAlice,30\nBob,25\n")

    file_content
    
    # Manually read the header line
    header_line = file_content.readline()
    assert header_line == "name,age\n"
    
    # Create DictReader after skipping the header manually
    reader = csv.DictReader(file_content, fieldnames=header_line.strip().split(","))
    
    row1 = next(reader)
    assert row1 == {'name': 'Alice', 'age': '30'}
    
    row2 = next(reader)
    assert row2 == {'name': 'Bob', 'age': '25'}


def test_ok_4():
    file_content_1 = StringIO("name,age\nAlice,30\nBob,25\n")
    file_content_2 = StringIO("name,age\nAlice,30\nBob,25\n")

    # Create DictReader after skipping the header manually
    reader = csv.DictReader(file_content_1)
    
    row1 = next(reader)
    assert row1 == {'name': 'Alice', 'age': '30'}

    file_content_2.readline() # <----------------- OK because readline is being called on a different file.


def test_violation_1():
    file_content = StringIO("name,age\nAlice,30\nBob,25\n")
    reader = csv.DictReader(file_content)
    next(reader)

    file_content.readline() # <----------------- VIOLATION calling readline directly on the file while using DictReader

def test_violation_2():
    content = """name,age
Alice,30
Bob,25
"""

    fileName = f'{uuid.uuid4()}.csv'
    with open(fileName, 'w') as f:
        f.write(content)

    file = open(fileName)
    reader = csv.DictReader(file)

    next(reader)
    file.readline() # <----------------- VIOLATION calling readline directly on the file while using DictReader

    file.close()
    os.remove(fileName)


expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
