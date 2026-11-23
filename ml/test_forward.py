import unittest
from types import SimpleNamespace
import numpy as np
from forward import probabilities


class ForwardTests(unittest.TestCase):
    def test_relu_and_stable_softmax(self):
        model = SimpleNamespace(
            coefs_=[np.eye(2), np.array([[1., 0., 0.], [0., 1., 0.]])],
            intercepts_=[np.zeros(2), np.full(3, 1000.)])
        actual = probabilities(model, np.array([[-2., 1.]]))
        expected = np.array([[1., np.e, 1.]]) / (2 + np.e)
        np.testing.assert_allclose(actual, expected)

    def test_nonfinite_output_is_withheld(self):
        model = SimpleNamespace(coefs_=[np.ones((1, 3))],
                                intercepts_=[np.array([np.nan, 0., 0.])])
        with self.assertRaisesRegex(ValueError, 'prediction withheld'):
            probabilities(model, np.ones((1, 1)))


if __name__ == '__main__':
    unittest.main()
