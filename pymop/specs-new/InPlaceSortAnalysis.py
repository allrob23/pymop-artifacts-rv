# ============================== Define spec ==============================
from pythonmop import Spec, call, TRUE_EVENT, FALSE_EVENT, VIOLATION, End, getKwOrPosArg
import builtins
import pythonmop.spec.spec as spec

# spec.DONT_MONITOR_PYTHONMOP = False

class InPlaceSortAnalysis(Spec):
    """
    Inplace sort is more efficient that sorted(). prefer using inplace if the original list is not needed.
    """

    should_skip_in_sites = True

    def __init__(self):
        super().__init__()
        self.stored_lists = set()  # TODO: change to dict for better information
        self.threshold = 1000

        @self.event_before(call(builtins, 'sorted'))
        def sorted(**kw):
            iterable = getKwOrPosArg('iterable', 0, kw)

            if hasattr(iterable, "__len__") and len(iterable) > self.threshold:
                self.stored_lists.add(id(iterable))
            return FALSE_EVENT
        
        @self.event_before(call(list, r'(__setitem__|append|extend|insert|pop|remove|clear|sort)' ))
        def modify_list(**kw):
            iterable = kw['obj']

            if len(self.stored_lists) > 0 and type(iterable) is list and id(iterable) in self.stored_lists:
                self.stored_lists.remove(id(iterable))
            return FALSE_EVENT

        @self.event_before(call(End, 'end_execution'))
        def end_execution(**kw):
            for l in self.stored_lists:
                return VIOLATION

    def match(self, call_file_name, call_line_num):
        # TODO: Provide more information about the lists that are being sorted.
        print(f'Spec - {self.__class__.__name__}: Unnessecary use of sorted() call at file {call_file_name}, line {call_line_num}.')
# =========================================================================

"""
spec_instance = InPlaceSortAnalysis()
spec_instance.create_monitor('D')

a = list(range(0, 32131))
b = list(range(0, 32132))
c = list(range(231, 321033))
d = list(range(0, 32134))
e = list(range(0, 32135))
f = list(range(0, 32136))
h = list(range(0, 32137))

sorted(a)  # DyLin warn
x = sorted(b)  # DyLin warn
y = sorted(c)  # DyLin warn
h = sorted(h, reverse=True)  # DyLin warn

d.sort()
z = sorted(e)
e.append([])
k = sorted(f)
f
h
print('end')
End().end_execution()
"""
