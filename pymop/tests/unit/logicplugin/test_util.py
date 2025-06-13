import pytest
from pythonmop.logicplugin.util import parseXMLOutput, generateXMLInput, FSMParseCategories, decodeArrows

class TestUtil:
    def test_parseXML(self):
        xmlStr = """
        <mop>
            <Events>event1 event2</Events>
            <Property>
                <Logic>ere</Logic>
                <Formula>some formula</Formula>
            </Property>
            <Message>MINIMIZED: minimized FSM formula</Message>
        </mop>
        """
        result = parseXMLOutput(xmlStr)
        assert result['logic'] == 'ere'
        assert result['formula'] == 'some formula'
        assert result['events'] == ['event1', 'event2']
        assert result['minimizedFSM'] == 'minimized FSM formula'

    def test_generateXMLInput(self):
        logic = 'ere'
        formula = 'some formula'
        events = ['event1', 'event2']
        xml_str = generateXMLInput(logic, formula, events)

        assert '<Logic>ere</Logic>' in xml_str
        assert '<Formula>some formula</Formula>' in xml_str
        assert '<Events>event1 event2</Events>' in xml_str

    def test_FSMParseCategories(self):
        formula = "state1 [ event1 [ state2 [ event2 ["
        categories = FSMParseCategories(formula)
        assert categories == ['state1', 'event1', 'state2', 'event2']

    def test_decodeArrows(self):
        formula = "a &gt; b &lt; c"
        decoded_formula = decodeArrows(formula)
        assert decoded_formula == "a > b < c"

    def test_parseXMLOutput_with_minimized_message(self):
        xmlStr = """
        <mop>
            <Events>event1 event2</Events>
            <Categories>state1 state2</Categories>
            <Property>
                <Logic>ere</Logic>
                <Formula>some formula</Formula>
            </Property>
            <Message>MINIMIZED: minimized FSM formula</Message>
        </mop>
        """
        result = parseXMLOutput(xmlStr)
        assert result['minimizedFSM'] == 'minimized FSM formula'

    def test_parseXMLOutput_without_minimized_message(self):
        xmlStr = """
        <mop>
            <Events>event1 event2</Events>
            <Categories>state1 state2</Categories>
            <Property>
                <Logic>ere</Logic>
                <Formula>some formula</Formula>
            </Property>
        </mop>
        """
        result = parseXMLOutput(xmlStr)
        assert result['events'] == ['event1', 'event2']
        assert result['categories'] == ['state1', 'state2']
        assert result['logic'] == 'ere'
        assert result['formula'] == 'some formula'

        assert result['minimizedFSM'] is None

    def test_parseXMLOutput_with_empty_events_and_categories(self):
        xmlStr = """
        <mop>
            <Events></Events>
            <Categories></Categories>
            <Property>
                <Logic>ere</Logic>
                <Formula>some formula</Formula>
            </Property>
            <Message>MINIMIZED: minimized FSM formula</Message>
        </mop>
        """
        result = parseXMLOutput(xmlStr)
        assert result['events'] == []
        assert result['categories'] == []

    def test_empty_formula(self):
        formula = ""
        result = FSMParseCategories(formula)
        assert result == []

    def test_single_category_with_space(self):
        formula = "mystate ["
        result = FSMParseCategories(formula)
        assert result == ["mystate"]

    def test_category_with_without_space(self):
        formula = "mystate["
        result = FSMParseCategories(formula)
        assert result == ["mystate"]

    def test_multiple_categories(self):
        formula = "state1 [ state2["
        result = FSMParseCategories(formula)
        assert result == ["state1", "state2"]

    def test_no_categories(self):
        formula = "no categories here"
        result = FSMParseCategories(formula)
        assert result == []

    def test_mixed_categories_and_text(self):
        formula = "state1 [ some text state2["
        result = FSMParseCategories(formula)
        assert result == ["state1", "state2"]

    def test_no_open_bracket(self):
        formula = "state1 state2"
        result = FSMParseCategories(formula)
        assert result == []

    def test_categories_and_whitespace(self):
        formula = "state1 [   state2["
        result = FSMParseCategories(formula)
        assert result == ["state1", "state2"]

    def test_categories_at_end(self):
        formula = "state1 [ state2[ category3 ["
        result = FSMParseCategories(formula)
        assert result == ["state1", "state2", "category3"]

    def test_categories_with_spaces(self):
        formula = "state1 [ state with space["
        result = FSMParseCategories(formula)
        assert result == ["state1", "space"]

    def test_complex_formula(self):
        formula = "state1 [ state2[ category3 [ state4 ["
        result = FSMParseCategories(formula)
        assert result == ["state1", "state2", "category3", "state4"]

    def test_logic_fsm_categories_none(self):
        logic = 'fsm'
        formula = 'state1 [ A ] && state2 [ B ]'
        events = ['A', 'B']

        xml_input = generateXMLInput(logic, formula, events)
        logic_data = parseXMLOutput(xml_input)

        assert logic_data['events'] == events
        assert logic_data['categories'] == FSMParseCategories(formula)
        assert logic_data['logic'] == logic
        assert logic_data['formula'] == formula

    def test_categories_not_none(self):
        logic = 'ere'
        formula = 'A && B'
        events = ['A', 'B']
        categories = ['state1', 'state2']

        xml_input = generateXMLInput(logic, formula, events, categories)
        logic_data = parseXMLOutput(xml_input)

        assert logic_data['events'] == events
        assert logic_data['categories'] == categories
        assert logic_data['logic'] == logic
        assert logic_data['formula'] == formula
