# ============================== Define spec ==============================
from pythonmop import Spec, call, getKwOrPosArg, TRUE_EVENT, FALSE_EVENT
import pythonmop.spec.spec as spec
import pythonmop.builtin_instrumentation as bi

# spec.DONT_MONITOR_PYTHONMOP = False
spec.DONT_MONITOR_SITE_PACKAGES = True


class UnsafeMapIterator(Spec):
    """
        Should not call next on iterator after modifying the map
    """
    should_skip_in_sites = True
    def __init__(self):
        super().__init__()

        @self.event_before(call(bi.InstrumentedDict, '__init__'))
        def createMap(**kw):
            pass

        @self.event_before(call(bi.InstrumentedDict, r'(__setitem__|update|pop|popitem|clear|setdefault|__delitem__)'))
        def updateMap(**kw):
            pass
        
        @self.event_before(call(bi.InstrumentedIterator, '__init__'), target = [1], names = [call(bi.InstrumentedDict, '*')])
        def createIter(**kw):
            iterable = getKwOrPosArg('iterable', 1, kw)

            if isinstance(iterable, bi.InstrumentedDict):
                return TRUE_EVENT
            
            return FALSE_EVENT

        @self.event_before(call(bi.InstrumentedIterator, '__next__'))
        def next(**kw):
            obj = kw['obj']

            if isinstance(obj.iterable, bi.InstrumentedDict):
                return TRUE_EVENT

            return FALSE_EVENT

    ere = 'createMap updateMap* createIter next* updateMap+ next'
    creation_events = ['createMap']

    def match(self, call_file_name, call_line_num):
        print(
            f'Spec - {self.__class__.__name__}: Should not call next on iterator after modifying the map . file {call_file_name}, line {call_line_num}.')
# =========================================================================


'''
spec_instance = UnsafeMapIterator()
spec_instance.create_monitor("B")

def run_experiment():
    map_1 = dict()
    map_2 = dict()

    map_1[1] = 12
    map_1[2] = 32

    map_2[1] = 19
    map_2[2] = 32

    iter_1_2 = iter(map_1)
    iter_2_2 = iter(map_2)

    iter(list())
    iter(list())

    map_1[1] = 1
    map_1[2] = 2

    next(iter_2_2) # should show no violation because map_2 was not modofied, but does show violation
    next(iter_1_2) # should show a violation since map_1 was modified

for i in range(50):
    run_experiment()
'''