# ============================== Define spec ==============================
from pythonmop import Spec, call, TRUE_EVENT, FALSE_EVENT
import builtins


class BuiltinAllAnalysis(Spec):
    """
    This is used to check if all builtins are used in the code.
    Converted from DyLin's BuiltinAllAnalysis checker.
    """

    def __init__(self):
        super().__init__()

        @self.event_after(call(builtins, 'all'))
        def violation(**kw):
            arg = kw['args'][0]
            if isinstance(arg, list):
                flattened = self._flatten(arg)
                if len(flattened) == 0 and kw['return_val'] == True:
                    return TRUE_EVENT
                else:
                    return FALSE_EVENT
            else:
                return FALSE_EVENT
            
        @self.event_after(call(builtins, 'any'))
        def violation(**kw):
            arg = kw['args'][0]
            if isinstance(arg, list):
                flattened = self._flatten(arg)
                if len(flattened) == 0 and kw['return_val'] == True:
                    return TRUE_EVENT
                else:
                    return FALSE_EVENT
            else:
                return FALSE_EVENT

    def _flatten(self, l):
        new_list = []
        for i in l:
            if isinstance(i, list):
                new_list = new_list + self._flatten(i)
            else:
                new_list.append(i)
        return new_list
    
    ere = 'violation'

    creation_events = ['violation']

    def match(self, call_file_name, call_line_num):
        print(f'Spec - {self.__class__.__name__}: Potentially unintended result for any() call at file {call_file_name}, line {call_line_num}.')
# =========================================================================
"""
spec_instance = BuiltinAllAnalysis()
spec_instance.create_monitor('D')

assert all([]) == True  # Violation
"""
