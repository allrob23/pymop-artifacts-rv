import itertools

def test_ok_1():
    """No violation where both child iterators are used."""
    parent_iter = iter([1, 2, 3, 4, 5])
    child1, child2 = itertools.tee(parent_iter, 2)

    # Consume both child1 and child2
    assert next(child1) == 1
    assert next(child2) == 1

    assert list(child1) == [2, 3, 4, 5]
    assert list(child2) == [2, 3, 4, 5]

# We do not yet support usages of iterator other than next(). The implementation is not trivial.
# def test_ok_1():
#     """No violation where both child iterators are used."""
#     parent_iter = iter([1, 2, 3, 4, 5])
#     child1, child2 = itertools.tee(parent_iter, 2)

#     assert list(child1) == [2, 3, 4, 5]
#     assert list(child2) == [2, 3, 4, 5]

def test_violation_1():
    """Violation where multiple iterators are created but only one is used."""
    parent_iter = iter([1, 2, 3, 4, 5])
    child1, child2, child3 = itertools.tee(parent_iter, 3)

    # Only consume child1, child2 and child3 are never used
    assert next(child1) == 1
    assert list(child1) == [2, 3, 4, 5]

def test_violation_2():
    """Violation where multiple iterators are created but none is used."""
    parent_iter = iter(range(1000))  # Large iterator
    child1, child2 = itertools.tee(parent_iter, 2)


# Because this spec depends on End event, all violations will
# be reported as if they happened in the last test case.
# Additionally, we'll be seeing only one violation because no formalism was used.
# To verify the correctness of the spec, you need to look into the output and find "Found 2 incorrect tee calls."
expected_violations_A = 1
expected_violations_B = [test_violation_2]
expected_violations_C = [test_violation_2]
expected_violations_C_plus = [test_violation_2]
expected_violations_D = [test_violation_2]

