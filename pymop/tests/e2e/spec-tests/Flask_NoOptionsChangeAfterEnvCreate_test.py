
from flask import Flask, render_template_string

# def test_ok_1():
#     app = Flask('App 1')

#     # Set custom Jinja options before the environment is created
#     app.jinja_options['variable_start_string'] = '<<'
#     app.jinja_options['variable_end_string'] = '>>'

#     # Access the Jinja environment to create it based on current jinja_options
#     env = app.jinja_env



def test_violation_1():
    app = Flask('App 2')

    # Set custom Jinja options before the environment is created
    app.jinja_options['variable_start_string'] = '<<'
    app.jinja_options['variable_end_string'] = '>>'

    # Access the Jinja environment to create it based on current jinja_options
    env = app.jinja_env

    # Attempt to change Jinja options after the environment is created
    app.jinja_options['variable_start_string'] = '{{' # VIOLATION
    app.jinja_options['variable_end_string'] = '}}'   # VIOLATION


expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_1]
expected_violations_C = [test_violation_1, test_violation_1]
expected_violations_C_plus = [test_violation_1, test_violation_1]
expected_violations_D = [test_violation_1, test_violation_1]
