import nltk
from nltk.classify.megam import config_megam, call_megam, write_megam_file
import os
from tempfile import NamedTemporaryFile
from nltk.classify import MaxentClassifier

MEGAMBINPATH = os.path.dirname(os.path.realpath(__file__)) + "/../bin/megam_i686.opt"

config_megam(MEGAMBINPATH)

# Sample training data
train_toks = [
    ({'feature1': 1.0}, 'label1'),
    ({'feature1': 5.0}, 'label2'),
]


classifier = MaxentClassifier.train(train_toks, algorithm='megam')

def test_ok_1():
    assert True == True, "Should be true"

def test_ok_2():
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=True, explicit=False)
        temp_file.flush()

        args = ['binary' , temp_file.name]
        call_megam(args)

def test_ok_3():
    # explicit=True
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=True, explicit=True)
        temp_file.flush()

        args = ['-explicit', 'binary' , temp_file.name]
        call_megam(args)

def test_ok_4():
    # bernoulli=False
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=False, explicit=False)
        temp_file.flush()

        args = ['-fvals', 'binary' , temp_file.name]
        call_megam(args)

def test_ok_5():
    # explicit=True and bernoulli=False
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=False, explicit=True)
        temp_file.flush()

        args = ['-fvals', '-explicit', 'binary' , temp_file.name]
        call_megam(args)

def test_ok_6():
    # missing -fvals option
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=False, explicit=False)
        temp_file.flush()

        args = ['binary' , temp_file.name]
        call_megam(args)

def test_violation_1():
    #  Missing -explicit option
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, bernoulli=True, explicit=True)
        temp_file.flush()

        args = ['binary' , temp_file.name]
        call_megam(args)

def test_violation_2():
    # missing both  -fvals and -explicit options
    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        write_megam_file(train_toks, classifier._encoding, temp_file, False, True)
        temp_file.flush()

        args = ['binary' , temp_file.name]
        call_megam(args)

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
