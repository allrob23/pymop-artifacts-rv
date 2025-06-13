from string import Template

def test_ok_1():
    # Create a template with a custom delimiter
    class MyTemplate(Template):
        delimiter = '%'


    # Change the delimiter
    template = MyTemplate('Hello')
    template.substitute(who='world')

def test_violation_1():
    # Create a template with a custom delimiter
    class MyTemplate(Template):
        delimiter = '%'

    template = MyTemplate('Hello')
    template.substitute(who='world')

    # Change the delimiter
    MyTemplate.delimiter = '#' # violation
    template.substitute(who='world')

def test_violation_2():
    # Create a template with a custom delimiter
    class MyTemplate(Template):
        delimiter = '%'

    template = MyTemplate('Hello')
    template.substitute(who='world')

    # Change the delimiter
    MyTemplate.delimiter = '#'  # violation
    template.safe_substitute()

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
