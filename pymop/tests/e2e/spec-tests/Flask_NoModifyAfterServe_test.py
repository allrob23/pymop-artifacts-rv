from flask import send_file, send_from_directory, Flask, jsonify, session
from flask.json.provider import DefaultJSONProvider
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



def test_violation_1():
    app = Flask('app 2')

    @app.route('/set_json_provider')
    def set_json_provider():
        app.json = DefaultJSONProvider(app)  # VIOLATION: Changing JSON provider during a request
        return jsonify(message="JSON provider changed.")
    
    with app.test_client() as client:
        client.get('/set_json_provider')



def test_violation_2():
    app = Flask('app 3')
    app.secret_key = 'supersecretkey'

    @app.route('/set_session_interface')
    def set_session_interface():
        from flask.sessions import SecureCookieSessionInterface
        app.session_interface = SecureCookieSessionInterface()  # VIOLATION: Changing session interface during a request
        session['data'] = 'This is session data'
        return "Session interface changed and data set."
    
    with app.test_client() as client:
        client.get('/set_session_interface')



def test_violation_3():
    app = Flask('app 4')

    @app.route('/set_config')
    def set_config():
        app.config['DEBUG'] = True  # Modifying configuration during a request
        return f"DEBUG mode set to {app.config['DEBUG']}"
        
    with app.test_client() as client:
        client.get('/set_config')


expected_violations_A = 12
expected_violations_B = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3, test_violation_3]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3, test_violation_3]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3, test_violation_3]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_2, test_violation_2, test_violation_2, test_violation_3, test_violation_3, test_violation_3, test_violation_3]
