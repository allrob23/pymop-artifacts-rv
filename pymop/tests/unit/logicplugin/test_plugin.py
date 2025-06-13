from pythonmop.logicplugin.plugin import FSMData, EREData, LTLData
import re


class TestPlugin:
    def test_fsm_data_initialization(self):
        formula = 'state1 [ A ] && state2 [ B ]'
        events = ['A', 'B']
        states = ['state1', 'state2']

        fsm_data = FSMData(formula, events, states)

        assert fsm_data.formula == formula
        assert fsm_data.events == events
        assert fsm_data.states == states

    def test_fsm_data_minimized(self):
        formula = "close+ manipulate+"
        events = ["close", "manipulate"]

        ere = EREData(formula, events)
        fsm = ere.toFSM()
        minimized_fsm = fsm.minimized()
        # assert minimized_fsm.formula == formula
        # assert minimized_fsm.events == events

    def test_ere_data_initialization(self):
        formula = "(next+ (remove | epsilon))*"
        events = ["next", "remove"]

        ere = EREData(formula, events)
        assert ere.formula == formula
        assert ere.events == events

    def test_ere_data_initialization2(self):
        formula = "close+ manipulate+"
        events = ["close", "manipulate"]

        ere = EREData(formula, events)
        assert ere.formula == formula
        assert ere.events == events

    def test_ltl_data_initialization(self):
        formula = "[](create => o (explicit or implicit))"
        events = ["create", "implicit", "explicit"]

        ltl_data = LTLData(formula, events)
        assert ltl_data.formula == formula
        assert ltl_data.events == events

    def test_ltl_data_initialization2(self):
        formula = "[](next => (*) hasnexttrue)"
        events = ["next", "hasnextfalse", "hasnexttrue"]

        ltl_data = LTLData(formula, events)
        assert ltl_data.formula == formula
        assert ltl_data.events == events

    def test_ere_to_fsm_conversion(self):
        # spec from OutputStreamWriter
        formula = "close+ manipulate+"
        events = ["close", "manipulate"]

        ere = EREData(formula, events)
        fsm = ere.toFSM()

        assert fsm.events == events
        assert len(fsm.states) == 3
        assert fsm.states == ["s0", "s1", "s2"]
        expected_fsm_formula = '''s0 [
   close -> s1
]
s1 [
   close -> s1
   manipulate -> s2
]
s2 [
   manipulate -> s2
]
alias match = s2'''
        assert fsm.formula == expected_fsm_formula

    def test_ltl_to_fsm_conversion(self):
        """
        this test failed when we ran the complete suit, but passed when we ran just it. This happens because the
        javamop plugin creates the names of the states (s0, s1...) different in each execution. To solve this we
        assert using regex in the name of the states...
        """
        formula = "[](next => (*) hasnexttrue)"
        events = ["next", "hasnextfalse", "hasnexttrue"]

        ltl = LTLData(formula, events)
        fsm = ltl.toFSM()

        assert fsm.events == events
        assert len(fsm.states) == 4
        expected_fsm_formula = r'''s\d\[
        hasnextfalse -> s\d
        next -> violation
        hasnexttrue -> s\d
        default s\d\]

        violation\[
        \]

        s\d\[
        hasnextfalse -> s\d
        next -> violation
        hasnexttrue -> s\d
        default s\d\]

        s\d\[
        hasnextfalse -> s\d
        next -> s\d
        hasnexttrue -> s\d
        default s\d\]'''
        for line in expected_fsm_formula.splitlines():
            # assert each line using regex
            line = line.strip()
            assert re.search(line, fsm.formula)

        # assert fsm.formula == expected_fsm_formula
