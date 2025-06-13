import ftplib


def test_ok_1():
    # Connect to the FTP server
    ftp = ftplib.FTP_TLS('ftp.pureftpd.org')
    ftp.login(user='user', passwd='password')

    ftp.prot_p()

    # List directory contents
    ftp.retrlines('LIST')

    # Close the connection
    ftp.quit()


def test_violation_1():
    # Connect to the FTP server
    ftp = ftplib.FTP_TLS('ftp.pureftpd.org')
    ftp.login(user='user', passwd='password')

    # Note: prot_p() is not called here, violating the requirement to secure the data connection

    # List directory contents
    ftp.retrlines('LIST')

    # Close the connection
    ftp.quit()
    

expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
