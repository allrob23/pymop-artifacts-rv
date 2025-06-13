import logging

def test_ok_1():
    logging.info("Info level log message.")
    logging.debug("Debug level log message after shutdown.")
    logging.critical("Critical level log message.")
    logging.warning("Warning level log message.")
    logging.fatal('sth fatal')
    logging.error('sth error')
    logging.exception('sth exception')
    logging.log(3, 'sth log')

def test_violation_1():
    logging.info("Info level log message.")
    logging.debug("Debug level log message after shutdown.")
    logging.critical("Critical level log message.")
    logging.warning("Warning level log message.")
    logging.fatal('sth fatal')

    # Everything after this would be a VIOLATION
    logging.shutdown()
    
    logging.info("Info level log message.")
    logging.debug("Debug level log message after shutdown.")
    logging.critical("Critical level log message.")
    logging.warning("Warning level log message.")
    logging.fatal('sth fatal')
    logging.error('sth error')
    logging.exception('sth exception')
    logging.log(3, 'sth log')


# Although we see only 8 violations in the test case,
# 2 of these methods internally call other monitored methods,
# for example .fatal internally calls .critical
expected_violations_A = 10
expected_violations_B = [test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1]
expected_violations_C = [test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1]
expected_violations_C_plus = [test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1]
expected_violations_D = [test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1, test_violation_1]
