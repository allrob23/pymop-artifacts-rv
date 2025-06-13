# ============================== Define spec ==============================
from pythonmop import Spec, call, TRUE_EVENT, FALSE_EVENT

class ItemInListAnalysis(Spec):
    """
    Checks if key in list is used.
    src: https://docs.quantifiedcode.com/python-anti-patterns/performance/using_key_in_list_to_check_if_key_is_contained_in_a_list.html
    """
    should_skip_in_sites = True

    def __init__(self):
        super().__init__()
        self.threshold = 100
        self.count = 5
        self.size_map = {}

        @self.event_after(call(list, '__contains__'))
        def list_contains(**kw):
            right = kw['args'][0]
            # print(f"{self.analysis_name} in {iid}")
            if type(right) == list and len(right) > self.threshold:
                uid = id(right) # id works here because we keep file into memory
                if uid not in self.size_map:
                    self.size_map[uid] = len(right)
                else:
                    self.size_map[uid] += len(right)
                if self.size_map[uid] > self.threshold * self.count:
                    return TRUE_EVENT
            return FALSE_EVENT

    ere = 'list_contains+'
    creation_events = ['list_contains']

    def match(self, call_file_name, call_line_num):
        print(
            f'Spec - {self.__class__.__name__}: checking key in list is less efficient than checking key in set. file {call_file_name}, line {call_line_num}.')
# =========================================================================


# spec_in = KeyInList()
# spec_in.create_monitor("D", True)

# list_1 = list([1, 2, 3, 4])
# 1 in list_1
# 2 in list_1
# 4 in list_1

# print('will create list')
# list_2 = [1, 2, 3, 4]
# 1 in list_2 # Doesn't work yet!

# set_1 = set([1, 2, 3, 4])
# 1 in set_1
