from nltk.probability import FreqDist, MLEProbDist, MutableProbDist

# Step 1: Create a frequency distribution
freq_dist = FreqDist({'A': 1, 'B': 20, 'C': 3})

# Step 2: Create a maximum likelihood estimate probability distribution
mle_prob_dist = MLEProbDist(freq_dist)

# Step 3: Convert to MutableProbDist
sample_list = list(freq_dist.keys())

def test_ok_1():
    assert True == True, "Should be true"

def test_ok_2():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)
    mutable_prob_dist.prob('A')

def test_ok_3():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)
    
    mutable_prob_dist.update('A', 0.2, False)
    mutable_prob_dist.update('B', 0.3, False)
    mutable_prob_dist.update('C', 0.5, False)

    mutable_prob_dist.prob('A')


def test_violation_1():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)

    mutable_prob_dist.update('A', 0.9, False) # Violation: sum of probabilities must be 1
    mutable_prob_dist.prob('A')

def test_violation_2():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)

    mutable_prob_dist.update('A', 0.9, False) # Violation: sum of probabilities must be 1
    mutable_prob_dist.max()

def test_violation_3():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)

    mutable_prob_dist.update('A', 0.1, False) # Violation: sum of probabilities must be 1
    mutable_prob_dist.discount()


def test_violation_4():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)

    mutable_prob_dist.update('A', 2, False) # Violation: sum of probabilities must be 1

    # will raise 2 violations because `generate` internally calls `prob` as well
    mutable_prob_dist.generate()

def test_violation_5():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list)

    mutable_prob_dist.update('A', -0.9991) # Violation: sum of probabilities must be 1
    mutable_prob_dist.logprob('A')

def test_violation_6():
    mutable_prob_dist = MutableProbDist(mle_prob_dist, samples=sample_list, store_logs=True)

    mutable_prob_dist.update('A', 0.1) # Violation: sum of probabilities must be 1
    mutable_prob_dist.prob('A')

expected_violations_A = 7
expected_violations_B = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_4, test_violation_5, test_violation_6]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_4, test_violation_5, test_violation_6]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_4, test_violation_5, test_violation_6]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_3, test_violation_4, test_violation_4, test_violation_5, test_violation_6]
