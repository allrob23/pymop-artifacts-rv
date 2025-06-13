import pytest

from pythonmop.monitor.formalismhandler.base import Base



def test_is_matched_method():
    formula = """
        s0 [
   getInstance -> s1
]
s1 [
   update -> s2
]
s2 [
   update -> s3
   reset -> s4
   digest -> s2
]
s3 [
   update -> s3
   reset -> s4
   digest -> s2
]
s4 [
   update -> s5
   reset -> s4
   digest -> s2
]
s5 [
   update -> s5
   digest -> s2
]
alias match = s2
        """
    base_instance = Base(formula)

    with pytest.raises(Exception) as exc_info:
        base_instance._is_matched()

    assert "ERROR: the _is_matched is not overwritten by the child class" in str(exc_info.value)
