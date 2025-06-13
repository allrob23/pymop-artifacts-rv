from pythonmop.monitor.formalismhandler.ere import Ere
from pythonmop.monitor.formalismhandler.ltl import Ltl


def test_ltl_fsm():
    # Arrange
    formula = """s0[
hasnextfalse -> s1
next -> violation
hasnexttrue -> s2
default s1
]
violation[
]
s1[
hasnextfalse -> s1
next -> violation
hasnexttrue -> s2
default s1
]
s2[
hasnextfalse -> s1
next -> s1
hasnexttrue -> s2
default s1
]"""
    ltl = Ltl(formula)

    # Act
    # Assert
    assert ltl.current_state == 's0'
    assert ltl._is_matched() == []


def test_ere_fsm():
    # Arrange
    formula = """s0 [
close -> s1
]
s1 [
]
alias match = s1"""
    ltl = Ere(formula)

    # Act
    # Assert
    assert ltl.current_state == 's0'
    assert ltl._is_matched() == []
