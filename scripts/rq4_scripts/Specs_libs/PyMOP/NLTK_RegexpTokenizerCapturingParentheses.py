# ============================== Define spec ==============================
from pythonmop import Spec, call, getKwOrPosArg, TRUE_EVENT, FALSE_EVENT
from nltk.tokenize import RegexpTokenizer
import re

def contains_capturing_groups(pattern):
    regex = re.compile(pattern)

    if regex.groups > 0:
        # Further check to distinguish capturing from non-capturing by examining the pattern
        # This involves checking all group occurrences in the pattern
        # We need to avoid matching escaped parentheses \( or \) and non-capturing groups (?: ...)
        non_capturing = re.finditer(r'\(\?[:=!]', pattern)
        non_capturing_indices = {match.start() for match in non_capturing}
        
        # Finding all parentheses that could start a group
        all_groups = re.finditer(r'\((?!\?)', pattern)
        for match in all_groups:
            if match.start() not in non_capturing_indices:
                return True  # Found at least one capturing group
        return False
    else:
        return False

class NLTK_RegexpTokenizerCapturingParentheses(Spec):
    """
    RegexpTokenizer pattern must not contain capturing parentheses
    src: https://www.nltk.org/api/nltk.tokenize.regexp.html
    """

    def __init__(self):
        super().__init__()

        @self.event_before(call(RegexpTokenizer, '__init__'))
        def regexpTokenizerCreated(**kw):
            pattern = getKwOrPosArg('pattern', 1, kw)

            if pattern is not None and contains_capturing_groups(pattern):
                return TRUE_EVENT
            return FALSE_EVENT
    
    ere = 'regexpTokenizerCreated+'
    creation_events = ['regexpTokenizerCreated']

    def match(self, call_file_name, call_line_num):
        print(
            f'Spec - {self.__class__.__name__}: Must use non_capturing parentheses for RegexpTokenizer pattern. file {call_file_name}, line {call_line_num}.')
# =========================================================================