import faulthandler
import sys
import threading
import io

def closeFileLater(file, timeout=1):
    # Use an event to signal the main thread that the timer is done
    done_event = threading.Event()

    # Define a function to close the file and signal completion
    def close_file():
        file.close()
        done_event.set()  # Signal that the file has been closed

    # Start a timer to close the file after 1 second
    threading.Timer(timeout, close_file).start()

    # Wait for the timer to signal it's done
    done_event.wait()


def test_ok_1():
    faulthandler.dump_traceback_later(1, False)

def test_ok_2():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(1, False, f)
    faulthandler.cancel_dump_traceback_later()
    f.close()

def test_ok_3():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(1, False, f)
    
    # closing file after traceback dump
    closeFileLater(f, 4)

def test_ok_4():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(1, repeat=True, file=f)

    done_event = threading.Event()
    def cancelTracebackDumpAndCloseFile():
        faulthandler.cancel_dump_traceback_later()
        f.close()
        done_event.set()

    threading.Timer(5, cancelTracebackDumpAndCloseFile).start()

    done_event.wait()

def test_violation_1():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(1, False, f)

    # closing file before traceback dump
    f.close()

def test_violation_2():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(3, False, f)
    
    # closing file before traceback dump
    closeFileLater(f, 1)

def test_violation_3():
    f = open("traceback.log", "w")
    faulthandler.dump_traceback_later(1, repeat=True, file=f)

    threading.Timer(5, faulthandler.cancel_dump_traceback_later).start()

    # closing file before traceback dump canceled
    closeFileLater(f, 4)

def test_violation_4():
    faulthandler.dump_traceback_later(1, False)

    # closing stderr before traceback dump
    sys.stderr.close()
    # reopen stderr to prevent program from crash
    sys.stderr = io.TextIOWrapper(io.FileIO(2, 'w'), write_through=True)

expected_violations_A = 7
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
