import tensorflow as tf

def test_ok_1():
    with open('def.txt', 'w'):
        pass

def test_ok_2():
    @tf.function
    def append_to_list(x):
        return x * x

    # Testing the monkey-patched tf.function
    print(append_to_list(tf.constant(2)))
    print(append_to_list(tf.constant(3)))
    print(append_to_list(tf.constant(2.0)))

def test_ok_3():
    @tf.function
    def append_to_list(x):
        return x * x

    # Testing the monkey-patched tf.function
    print(append_to_list(tf.constant(2)))
    print(append_to_list(tf.constant(3)))
    print(append_to_list(tf.constant(2.0)))

    print('hi')

def test_ok_4():
    def nested_1():
        def nested_2():
            def nested_3():
                @tf.function
                def append_to_list(x):
                    mylist = [2, 3]
                    mylist.append(x) # ok list is defined within the tf.function
                    return x * x

                # Testing the monkey-patched tf.function
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))

            nested_3()
        nested_2()
    nested_1()

def test_violation_1():
    @tf.function
    def append_to_list(x):
        with open('abc.txt', 'w'):
            pass
        return x * x

    # Testing the monkey-patched tf.function
    print(append_to_list(tf.constant(2)))

def test_violation_2():
    @tf.function
    def append_to_list(x):
        print('hi') # violation (side effect in a tf.function)
        return x * x

    # Testing the monkey-patched tf.function
    append_to_list(tf.constant(2))

mylist = [2, 3]
def test_violation_3():
    def nested_1():
        def nested_2():
            def nested_3():
                @tf.function
                def append_to_list(x):
                    mylist.append(x) # violation (side effect in a tf.function)
                    return x * x

                # Testing the monkey-patched tf.function
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))

            nested_3()
        nested_2()
    nested_1()

def test_violation_4():
    mylist = []
    def nested_1():
        def nested_2():
            def nested_3():
                @tf.function
                def append_to_list(x):
                    mylist.append(x) # violation (side effect in a tf.function)
                    return x * x

                # Testing the monkey-patched tf.function
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))
                append_to_list(tf.constant(2))

            nested_3()
        nested_2()
    nested_1()

expected_violations_A = 4
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4]
