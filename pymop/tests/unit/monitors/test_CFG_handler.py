from pythonmop.monitor.formalismhandler.cfg import Cfg

import unittest
import nltk


class TestCFGHandler(unittest.TestCase):

    def test_case_convert_cfg_1(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = """
            S -> a A c,
            A -> b A c | epsilon
        """
        expected = "S -> 'a' A 'c'\nA -> 'b' A 'c' | epsilon"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance.convert_cfg(input))

    def test_case_convert_cfg_2(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = """
            S -> x | x A | epsilon,
            A -> 'x' y | epsilon
        """
        expected = "S -> 'x' | 'x' A | epsilon\nA -> 'x' 'y' | epsilon"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance.convert_cfg(input))

    def test_case_convert_cfg_3(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = """
            S -> a S b | A b | epsilon,
            A -> c A | epsilon
        """
        expected = "S -> 'a' S 'b' | A 'b' | epsilon\nA -> 'c' A | epsilon"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance.convert_cfg(input))

    def test_case_parse_grammar_1(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = "S -> 'a' S 'b' | 'c' | epsilon"
        expected = {'S': [("'a'", 'S', "'b'"), ("'c'",), ()]}

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._parse_grammar(input))

    def test_case_parse_grammar_2(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = "S -> 'a' S | epsilon\nA -> 'a' | 'b'"
        expected = {'S': [("'a'", 'S'), ()], 'A': [("'a'",), ("'b'",)]}

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._parse_grammar(input))

    def test_case_parse_grammar_3(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = "S -> 'a' S 'b' | A\nA -> 'c'"
        expected = {'S': [("'a'", 'S', "'b'"), ('A',)], 'A': [("'c'",)]}

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._parse_grammar(input))

    def test_case_eliminate_left_recursion_1(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output (A simple left recursion in this case)
        input = {'S': [('S', "'a'"), ("'b'",)]}
        expected = {
            'S': [("'b'", 'S_added')],
            'S_added': [("'a'", 'S_added'), ()]
        }

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._eliminate_left_recursion(input))

    def test_case_eliminate_left_recursion_2(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output (No left recursion in this case)
        input = {'S': [("'a'", 'A'), ("'b'",)], 'A': [("'c'",)]}
        expected = {'S': [("'a'", 'A'), ("'b'",)], 'A': [("'c'",)]}

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._eliminate_left_recursion(input))

    def test_case_eliminate_left_recursion_3(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output (Multiple rules with left recursion in this case)
        input = {
            'S': [('S', 'A'), ('S', "'b'"), ("'c'",)],
            'A': [("'d'",)]
        }
        expected = {
            'S': [("'c'", 'S_added')],
            'S_added': [('A', 'S_added'), ("'b'", 'S_added'), ()],
            'A': [("'d'",)]
        }

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._eliminate_left_recursion(input))

    def test_case_format_grammar_1(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = {'S': [("'a'", 'S', "'b'"), ("'c'",)]}
        expected = "S -> 'a' S 'b'|'c'"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._format_grammar(input))

    def test_case_format_grammar_2(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = {'S': [("'a'",), ()], 'A': [("'b'",)]}
        expected = "S -> 'a'|\nA -> 'b'"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._format_grammar(input))

    def test_case_format_grammar_3(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define the input and expected output
        input = {
            'S': [("'a'", 'S_added'), ("'b'",)],
            'S_added': [("'c'", 'S_added'), ()]
        }
        expected = "S -> 'a' S_added|'b'\nS_added -> 'c' S_added|"

        # Call the method and check if it returns the expected output
        self.assertEqual(expected, mock_instance._format_grammar(input))

    def test_case_compute_c_sets_1(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define input and expected output
        input = "S -> 'a'"
        expected = {'S': set(),
                    'a': set()}

        # Call the method and check if it returns the expected output
        cfg = nltk.CFG.fromstring(input)
        C = mock_instance.compute_c_sets(cfg, mock_instance.compute_g_sets(cfg))

        self.assertEqual(expected, C)

    def test_case_compute_c_sets_2(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define input and expected output
        input = "S -> 'a' A\nA -> 'b' B\nB -> 'c'"
        expected = {'S': set(),
                    'A': set(),
                    'B': set(),
                    'a': {frozenset({'c', 'b'})},
                    'b': {frozenset({'c'})},
                    'c': set()}

        # Call the method and check if it returns the expected output
        cfg = nltk.CFG.fromstring(input)
        C = mock_instance.compute_c_sets(cfg, mock_instance.compute_g_sets(cfg))

        self.assertEqual(expected, C)

    def test_case_compute_c_sets_3(self):
        # Initialize a mock instance of Cfg
        mock_instance = Cfg("", None, False, True)

        # Define input and expected output
        input = "S -> A B | C\nA -> 'a' A | \nB -> 'b' B | 'd'\nC -> 'e' F\nF -> 'f' F | 'g'"
        expected = {                    'S': set(),
                    'A': {frozenset({'b', 'd'}), frozenset({'d'})},
                    'B': set(),
                    'C': set(),
                    'F': set(),
                    'a': {frozenset({'b', 'a', 'd'}), frozenset({'b', 'd'}), frozenset({'d'}),frozenset({'a', 'd'})},
                    'b': {frozenset({'b', 'd'}), frozenset({'d'})},
                    'd': set(), 'f': {frozenset({'g'}), frozenset({'g', 'f'})}, 
                    'e': {frozenset({'g'}), frozenset({'g', 'f'})}, 'g': set()}

        # Call the method and check if it returns the expected output
        cfg = nltk.CFG.fromstring(input)
        C = mock_instance.compute_c_sets(cfg, mock_instance.compute_g_sets(cfg))

        self.assertEqual(expected, C)

    def test_case_comprehensive_1(self):
        rules_str = """
            S -> 'b' S 'b' | 'b' A 'b' | epsilon
            A -> A 'a' | 'a'
        """

        # Test with a set of input strings
        test_strings = [
            ("b b a b b", ['', 'match', '', '', 'match']),
            ("b a b", ['', '', 'match']),
            ("b b a a b b", ['', 'match', '', '', '', 'match']),
            ("a b", ['fail', 'fail']),
            ("b a a b", ['', '', '', 'match']),
            ("b b a b", ['', 'match', '', ''])
        ]

        # Check each input string
        for input_string, expected in test_strings:
            instance = Cfg(rules_str)
            input_words = input_string.split()
            for i in range(len(input_words)):
                result = instance.transition(input_words[i])
                if expected[i] == '':
                    self.assertEqual([], result)
                else:
                    self.assertEqual([expected[i]], result)

    def test_case_comprehensive_2(self):
        rules_str = """
            S -> 'if' '(' E ')' 'then' S 'else' S | E
            E -> E '+' T | T
            T -> T '*' F | F
            F -> '(' E ')' | 'num'
        """

        # Test with a set of input strings
        test_strings = [
            ("if ( num + num ) then num else num", ['', '', '', '', '', '', '', '', '', 'match']),
            ("if ( num ) then if ( num ) then num else num else num", ['', '', '', '', '', '', '', '', '', '', '', '',
                                                                       '', '', 'match']),
            ("num + num * num", ['match', '', 'match', '', 'match']),
            ("+ num + num * num", ['fail', 'fail', 'fail', 'fail', 'fail', 'fail']),
            ("( num + num ) * num", ['', '', '', '', 'match', '', 'match']),
            ("if ( num + num ) then num else ( num * num )", ['', '', '', '', '', '', '', '', '', '', '', '', '',
                                                              'match']),
            ("if ( num ) then ( num + num ) else ( num * num )", ['', '', '', '', '', '', '', '', '', '', '', '',
                                                                  '', '', '', 'match']),
            ("if ( ( num + num ) * num ) then num else num", ['', '', '', '', '', '', '', '', '', '', '', '', '',
                                                              'match'])
        ]

        # Check each input string
        for input_string, expected in test_strings:
            instance = Cfg(rules_str)
            input_words = input_string.split()
            for i in range(len(input_words)):
                result = instance.transition(input_words[i])
                if expected[i] == '':
                    self.assertEqual([], result)
                else:
                    self.assertEqual([expected[i]], result)
