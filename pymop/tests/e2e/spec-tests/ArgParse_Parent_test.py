import argparse

def test_ok_1():
    # Define a parent parser
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--parent_arg', help='Parent argument')

    # Define a child parser inheriting from the parent parser
    child_parser = argparse.ArgumentParser(parents=[parent_parser])
    child_parser.add_argument('--child_arg', help='Child argument')

    # Parse arguments
    args = child_parser.parse_args()

def test_violation_1():
    # Define a parent parser
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--parent_arg', help='Parent argument')

    # Define a child parser inheriting from the parent parser
    child_parser = argparse.ArgumentParser(parents=[parent_parser])
    child_parser.add_argument('--child_arg', help='Child argument')

    # Now, let's make a change to the parent parser after it's been used in the child parser
    parent_parser.add_argument('--new_parent_arg', help='New parent argument')

    # Parse arguments
    args = child_parser.parse_args()

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]

