from flask import send_file, send_from_directory, Flask
import time

with open('./test.txt', 'w') as f:
    f.write('test')


def test_ok_1():
    time.sleep(0.5)
    app = Flask('app 1')


    @app.route('/safe-download-1')
    def safe_download_1():
        return send_file(
            f'./test.txt',                                     # OK
            as_attachment=True,
            download_name='example.pdf'
        )
    
    with app.test_client() as client:
        client.get('/safe-download-1')

def test_ok_2():
    time.sleep(1)

    app = Flask('app 2')

    @app.route('/safe-download-2/<filename>')
    def safe_download_2(filename):
        return send_from_directory(
            './',                                               # OK
            f'./{filename}'
        )
    
    with app.test_client() as client:
        client.get('/safe-download-2/test.txt')


def test_violation_1():
    time.sleep(1.5)

    app = Flask('app 3')

    @app.route('/unsafe-download/<filename>')
    def unsafe_download(filename):
        return send_file(
            filename,                                            # VIOLATION
            as_attachment=True,
            download_name='example.pdf'
        )
    
    with app.test_client() as client:
        client.get('/unsafe-download/test.txt')

# the violation appearing 3 times is expected because we have 3 parametric
# combintions where flask module is bound to each of Flask instances.
# when an event that's triggered by hte flask module causes a violatition,
# all 3 combinations raise a violation.
expected_violations_A = 3
expected_violations_B = [test_violation_1, test_violation_1, test_violation_1]
expected_violations_C = [test_violation_1, test_violation_1, test_violation_1]
expected_violations_C_plus = [test_violation_1, test_violation_1, test_violation_1]
expected_violations_D = [test_violation_1, test_violation_1, test_violation_1]
