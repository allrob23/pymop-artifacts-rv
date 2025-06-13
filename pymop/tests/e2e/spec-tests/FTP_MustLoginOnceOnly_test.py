from ftplib import FTP, error_perm
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
import threading
import time

# Step 1: Create a function to start an FTP server using pyftpdlib
def start_ftp_server():
    # Set up a virtual user with access to a specific directory
    authorizer = DummyAuthorizer()
    authorizer.add_user("testuser1", "password1", "/", perm="elradfmw")
    authorizer.add_user("testuser2", "password2", "/", perm="elradfmw")
    authorizer.add_user("testuser3", "password3", "/", perm="elradfmw")
    authorizer.add_user("testuser4", "password4", "/", perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    # Start the FTP server on localhost, port 2121
    server = FTPServer(("127.0.0.1", 2121), handler)
    server.serve_forever()

# Step 2: Start the FTP server in a separate thread
ftp_server_thread = threading.Thread(target=start_ftp_server)
ftp_server_thread.daemon = True
ftp_server_thread.start()

# Give the server a moment to start
time.sleep(1)

def test_ok_1():
    # Connect to the local FTP server
    ftp = FTP()
    ftp.connect("127.0.0.1", 2121)
    ftp.login(user='testuser1', passwd='password1')  # First login OK

    ftp.quit()

def test_ok_2():
    # Connect to the local FTP server
    ftp1 = FTP()
    ftp2 = FTP()
    ftp1.connect("127.0.0.1", 2121)
    ftp2.connect("127.0.0.1", 2121)
    ftp1.login(user='testuser1', passwd='password1')  # First login OK
    ftp2.login(user='testuser2', passwd='password2')  # First login OK

    ftp1.quit()
    ftp2.quit()

def test_violation_1():
    # Connect to the local FTP server
    ftp = FTP()
    ftp.connect("127.0.0.1", 2121)
    ftp.login(user='testuser1', passwd='password1')  # First login OK
    ftp.login(user='testuser2', passwd='password2')  # Second login VIOLATION

    ftp.quit()

def test_violation_2():
    # Connect to the local FTP server
    ftp = FTP()
    ftp.connect("127.0.0.1", 2121)
    ftp.login(user='testuser1', passwd='password1')  # First login OK
    ftp.login(user='testuser2', passwd='password2')  # Second login VIOLATION
    ftp.login(user='testuser2', passwd='password2')  # VIOLATION
    ftp.login(user='testuser3', passwd='password3')  # VIOLATION
    ftp.login(user='testuser4', passwd='password4')  # VIOLATION

    ftp.quit()

def test_violation_3():
    # Connect to the local FTP server
    ftp1 = FTP()
    ftp2 = FTP()
    ftp1.connect("127.0.0.1", 2121)
    ftp2.connect("127.0.0.1", 2121)
    ftp1.login(user='testuser1', passwd='password1')  # First login OK
    ftp2.login(user='testuser1', passwd='password1')  # First login OK
    ftp1.login(user='testuser2', passwd='password2')  # VIOLATION
    ftp1.login(user='testuser3', passwd='password3')  # VIOLATION
    ftp1.login(user='testuser1', passwd='password1')  # VIOLATION
    
    ftp1.quit()
    ftp2.quit()


expected_violations_A = 8
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3]
