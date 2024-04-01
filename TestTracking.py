import unittest

import numpy as np
from misc import boxes_center


class TestBoxesCenter(unittest.TestCase):

    def test_single(self):
        corners = np.array([[1, 2, 3, 4]])
        expected = np.array([[2, 3]])
        np.testing.assert_array_equal((boxes_center(corners)), expected)

    def test_many(self):
        corners = np.array([[1, 1, 3, 3],
                            [3, 3, 1, 1]])
        expected = np.array([[2, 2],
                             [2, 2]])
        np.testing.assert_array_equal((boxes_center(corners)), expected)


if __name__ == "__main__":
    unittest.main()
