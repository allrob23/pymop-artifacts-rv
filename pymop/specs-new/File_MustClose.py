# ============================== Define spec ==============================
from pythonmop import Spec, call, getStackTrace, parseStackTrace, End
import builtins
import inspect

class MonitoredFile():
    def __init__(self, originalFile):
        self.originalFile = originalFile

    def open(self, file, stackTrace):
        pass

    def close(self, *args, **kwargs):
        pass

# ========== Override builtins open =============
# These are used to prevent infinite recursion
# when the monitored method is used within our
# event handling implementation
alreadyWithinOpen = False
alreadyWithinClose = False

originalOpen = builtins.open

def customOpen(*args, **kwargs):
    global alreadyWithinOpen
    if alreadyWithinOpen:
        return originalOpen(*args, **kwargs)

    originalFile = originalOpen(*args, **kwargs)
    monitoredFile = MonitoredFile(originalFile)
    originalClose = originalFile.close

    # find the path of the file calling this function and the line
    stackTrace = parseStackTrace(getStackTrace())

    if '_pytest/logging.py' not in stackTrace and 'monitor/monitor_a.py' not in stackTrace:
        alreadyWithinOpen = True
        monitoredFile.open(originalFile, stackTrace)
        alreadyWithinOpen = False

    def customClose(*args, **kwargs):
        global alreadyWithinClose
        if alreadyWithinClose:
            return originalClose(*args, **kwargs)
        
        alreadyWithinClose = True
        monitoredFile.close(*args, **kwargs)
        alreadyWithinClose = False
        return originalClose(*args, **kwargs)

    originalFile.close = customClose

    return originalFile

builtins.open = customOpen
# =================================================

class File_MustClose(Spec):
    """
    TODO: Add description here.
    """
    def __init__(self):
        # self.end_state_violation = True
        self.opened = {}
        self.openStackTrace = {}
        super().__init__()

        # open method
        @self.event_before(call(MonitoredFile, 'open'))
        def open(**kw):
            file = kw['args'][1]
            stackTrace = kw['args'][2]

            self.opened[file] = True
            self.openStackTrace[file] = stackTrace

        # close method
        @self.event_before(call(MonitoredFile, 'close'))
        def close(**kw):
            file = kw['obj'].originalFile

            if file in self.opened:
                del self.opened[file]
        
        @self.event_after(call(End, 'end_execution'))
        def end(**kw):
            pass

    fsm = '''
        s0 [
            open -> s1
        ]
        s1 [
            close -> s0
            end -> s2
        ]
        s2 [
            default s2
        ]
        alias match = s2
    '''
    creation_events = ['open']

    def match(self, call_file_name, call_line_num):
        size = len(self.opened)
        print(f'Spec - {self.__class__.__name__}: You forgot to close {size} files.')
        for file in self.opened:
            print(f'File {file} opened at {self.openStackTrace[file]}')
# =========================================================================

'''
spec_in = File_MustClose()
spec_in.create_monitor("File_MustClose")

t = open("test.txt", "w")
# forgot to close the file t

with open("test2.txt", "w") as t1:
    # Any code that uses the resource
    pass
# exiting the block automatically closes the other file t1

spec_in.end()
'''