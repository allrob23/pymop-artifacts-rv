import nltk
from nltk.translate import AlignedSent, IBMModel1, IBMModel2, IBMModel3, IBMModel4, IBMModel5

# Example bilingual sentence pairs (German to English)
bitext = [
    AlignedSent(['klein', 'ist', 'das', 'haus'], ['the', 'house', 'is', 'small']),
    AlignedSent(['das', 'haus', 'ist', 'ja', 'groß'], ['the', 'house', 'is', 'big']),
    AlignedSent(['das', 'buch', 'ist', 'ja', 'klein'], ['the', 'book', 'is', 'small']),
    AlignedSent(['das', 'haus'], ['the', 'house']),
    AlignedSent(['das', 'buch'], ['the', 'book']),
    AlignedSent(['ein', 'buch'], ['a', 'book'])
]

def test_ok_1():
    assert True == True, "Should be true"

def test_ok_2():
    IBMModel1(bitext, 5)

def test_ok_3():
    IBMModel2(bitext, 5)

def test_ok_4():
    IBMModel3(bitext, 5)

def test_ok_5():
    try:
        IBMModel4(bitext, 5)
    except:
        pass
    
def test_ok_6():
    try:
        IBMModel5(bitext, 5)
    except:
        pass

def test_violation_1():
    try:
        IBMModel1(bitext, 5, probability_tables={})
    except:
        pass

def test_violation_2():
    try:
        IBMModel2(bitext, 5, {})
    except:
        pass
    
def test_violation_3():
    try:
        IBMModel3(bitext, 5, probability_tables={})
    except:
        pass

def test_violation_4():
    try:
        IBMModel4(bitext, 5, {}, {})
    except:
        pass

def test_violation_5():
    try:
        IBMModel5(bitext, 5, probability_tables={}, source_word_classes={}, target_word_classes={})
    except:
        pass

expected_violations_A = 31
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_5]
