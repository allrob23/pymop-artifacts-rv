import itertools

def test_ok_1():
    """Test correct usage where parent iterator is not advanced after tee."""
    parent_iter = iter([1, 2, 3, 4, 5])
    child1, child2 = itertools.tee(parent_iter, 2)

    # Consume from child1 and child2 independently
    assert next(child1) == 1
    assert next(child2) == 1

    assert list(child1) == [2, 3, 4, 5]
    assert list(child2) == [2, 3, 4, 5]

def test_ok_2():
    """Correct usage after partially consuming the parent iterator before tee."""
    parent_iter = iter([1, 2, 3, 4, 5])

    # Consume one item from the parent iterator
    assert next(parent_iter) == 1

    # Create child iterators from the current state of parent_iter
    child1, child2 = itertools.tee(parent_iter, 2)

    # Now children correctly start from 2
    assert next(child1) == 2
    assert next(child2) == 2

    assert list(child1) == [3, 4, 5]
    assert list(child2) == [3, 4, 5]

def test_violation_1():
    """Test incorrect usage where parent iterator is consumed after tee."""
    parent_iter = iter([1, 2, 3, 4, 5])
    child1, child2 = itertools.tee(parent_iter, 2)

    # Consuming from the parent iterator directly
    assert next(parent_iter) == 1  # <----------- VIOLATION HERE: This causes child1 and child2 to skip 1

    # Child iterators start from 2, not 1
    assert next(child1) == 2
    assert next(child2) == 2


def test_violation_2():
    """Test incorrect usage where parent iterator is consumed after tee."""
    parent_iter_1 = iter([1, 2, 3, 4, 5])
    parent_iter_2 = iter([1, 2, 3, 4, 5])

    child1, child2 = itertools.tee(parent_iter_1, 2)
    child3, child4 = itertools.tee(parent_iter_2, 2)

    # Consuming from the parent iterator directly
    assert next(parent_iter_1) == 1  # <----------- VIOLATION HERE: This causes child1 and child2 to skip 1

    # Child iterators start from 2, not 1
    assert next(child1) == 2
    assert next(child2) == 2

    # Child iterators 3 and 4 start from 1 because parent_iter_2 is not consumed
    assert next(child3) == 1
    assert next(child4) == 1

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
