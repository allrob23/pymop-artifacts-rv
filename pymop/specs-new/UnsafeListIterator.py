# ============================== Define spec ==============================
from pythonmop import Spec, call, getKwOrPosArg, TRUE_EVENT, FALSE_EVENT
import pythonmop.spec.spec as spec
import pythonmop.builtin_instrumentation as bi

# spec.DONT_MONITOR_PYTHONMOP = False
spec.DONT_MONITOR_SITE_PACKAGES = True

class UnsafeListIterator(Spec):
    """
    Should not call next on iterator after modifying the list
    """
    should_skip_in_sites = True
    def __init__(self):
        super().__init__()

        @self.event_before(call(list, '__init__'))
        def createList(**kw):
            pass

        @self.event_before(call(list, r'(__setitem__|append|extend|insert|pop|remove|clear|sort)' ))
        def updateList(**kw):
            pass
        
        @self.event_before(call(bi.InstrumentedIterator, '__init__'), target = [1], names = [call(list, '*')])
        def createIter(**kw):
            iterable = getKwOrPosArg('iterable', 1, kw)

            if isinstance(iterable, list):
                return TRUE_EVENT
            
            return FALSE_EVENT

        @self.event_before(call(bi.InstrumentedIterator, '__next__'))
        def next(**kw):
            obj = kw['obj']

            if isinstance(obj.iterable, list):
                return TRUE_EVENT

            return FALSE_EVENT

    ere = 'createList updateList* createIter next* updateList+ next'
    creation_events = ['createList']

    def match(self, call_file_name, call_line_num):
        print(
            f'Spec - {self.__class__.__name__}: Should not call next on iterator after modifying the list. file {call_file_name}, line {call_line_num}.')
# =========================================================================

'''
spec_instance = UnsafeListIterator()
spec_instance.create_monitor("D")

list_1 = list()
list_2 = list()

list_1.append(12)
list_1.append(32)

list_2.append(19)
list_2.append(32)

iter_1 = iter(list_1)
iter_2 = iter(list_2)

list_1[0] = 1
list_1.append(22)

next(iter_2)  # should show no violation because list_2 was not modified
next(iter_1)  # should show a violation since list_1 was modified
'''