import numpy as np
import scipy.integrate


def test_ok_1():
    mu1 = 0
    mu2 = 0
    std1 = 1
    std2 = 1

    def integral_fun(x):
        nor1 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std1)) * (np.e ** ((-(x - mu1) ** 2) / (2 * std1 ** 2))))
        nor2 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std2)) * (np.e ** ((-(x - mu2) ** 2) / (2 * std2 ** 2))))
        return nor1 + nor2

    print(scipy.integrate.quad(integral_fun, 0, 5))


def test_ok_2():
    mu1 = 0
    mu2 = 0
    std1 = 1
    std2 = 1

    def integral_fun(x):
        nor1 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std1)) * (np.e ** ((-(x - mu1) ** 2) / (2 * std1 ** 2))))
        nor2 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std2)) * (np.e ** ((-(x - mu2) ** 2) / (2 * std2 ** 2))))
        return nor1 + nor2

    print(scipy.integrate.quad(integral_fun, -100000, 100000))


def test_ok_3():
    mu1 = 0
    mu2 = 0
    std1 = 1
    std2 = 1

    def integral_fun(x):
        nor1 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std1)) * (np.e ** ((-(x - mu1) ** 2) / (2 * std1 ** 2))))
        nor2 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std2)) * (np.e ** ((-(x - mu2) ** 2) / (2 * std2 ** 2))))
        return nor1 + nor2

    print(scipy.integrate.quad(integral_fun, -np.inf, np.inf))


def test_violation_1():
    mu1 = 0
    mu2 = 0
    std1 = 1
    std2 = 1

    def integral_fun(x):
        nor1 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std1)) * (np.e ** ((-(x - mu1) ** 2) / (2 * std1 ** 2))))
        nor2 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std2)) * (np.e ** ((-(x - mu2) ** 2) / (2 * std2 ** 2))))
        return nor1 + nor2

    print(scipy.integrate.quad(integral_fun, np.inf, 100001))


def test_violation_2():
    mu1 = 0
    mu2 = 0
    std1 = 1
    std2 = 1

    def integral_fun(x):
        nor1 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std1)) * (np.e ** ((-(x - mu1) ** 2) / (2 * std1 ** 2))))
        nor2 = 0.5 * ((1 / (np.sqrt(2 * np.pi) * std2)) * (np.e ** ((-(x - mu2) ** 2) / (2 * std2 ** 2))))
        return nor1 + nor2

    print(scipy.integrate.quad(integral_fun, -100001, np.inf))

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
