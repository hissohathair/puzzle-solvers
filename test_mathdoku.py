# test_mathdoku.py

import unittest
import mathdoku as md

TEST_GRID_SIZE = 4
TEST_CAGES = [
    (16, '*', 3),
    (7, '+', 3),
    (2, '-', 2),
    (12, '*', 3),
    (2, '/', 2),
    (2, '/', 2),
    (4, '=', 1)
]
TEST_CAGE_MAP = [
    [0, 0, 1, 1],
    [2, 0, 1, 6],
    [2, 3, 4, 4],
    [3, 3, 5, 5],
]
TEST_CAGE_POSSIBILITIES = [
    [(1, 4, 4), (2, 2, 4)],  # (16, '*', 3),
    [(1, 2, 4), (1, 3, 3), (2, 2, 3)],  # (7, '+', 3),
    [(3, 1), (4, 2)],        # (2, '-', 2),
    [(1, 3, 4), (2, 2, 3)],  # (12, '*', 3),
    [(2, 1), (4, 2)],        # (2, '/', 2),
    [(2, 1), (4, 2)],        # (2, '/', 2),
    [(4,)],                  # (4, '=', 1)
]
SOLUTION = [
    [2, 4, 1, 3],
    [1, 2, 3, 4],
    [3, 1, 4, 2],
    [4, 3, 2, 1],
]


class TestFunctions(unittest.TestCase):
    """Test the helper functions"""

    def test_product(self):
        """Test product function"""
        test_cases = [
            [16, [4, 4]],
            [16, [4, 2, 2]],
            [32, [4, 4, 2]],
            [32, [4, 2, 2, 2, 1]],
            [1, [1, 1, 1, 1]],
            [2, [1, 1, 2, 1]],
            [0, [6, 6, 6, 0]],
            [362880, [9, 8, 7, 6, 5, 4, 3, 2]],
            [362880, [2, 3, 4, 5, 6, 7, 8, 9]],
            [1, [1]],
        ]
        for tc in test_cases:
            target, numlist = tc
            self.assertEqual(target, md.product(numlist))
        return

    def test_subtract(self):
        """Test subtract function"""
        test_cases = [
            [2, [4, 2]],
            [2, [3, 1]],
            [-2, [1, 3]],
            [-27, [9, 8, 7, 6, 5, 4, 3, 2, 1]],
            [0, [1, 1]],
            [1, [1]],
        ]
        for tc in test_cases:
            target, numlist = tc
            self.assertEqual(target, md.subtract(numlist))
        return

    def test_divide(self):
        """Test divide function"""
        test_cases = [
            [2, [4, 2]],
            [1, [4, 4]],
            [1, [4, 2, 2]],
            [3, [9, 3]],
            [1, [362880, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
            [1, [1]],
        ]
        for tc in test_cases:
            target, numlist = tc
            self.assertEqual(target, md.divide(numlist))
        return


class TestMathDoku(unittest.TestCase):

    def setUp(self):
        """Test fixtures"""
        self.m = md.MathDoku(grid_size=TEST_GRID_SIZE)
        self.m.init_puzzle(cages=TEST_CAGES, cage_map=TEST_CAGE_MAP)
        return

    def test_init(self):
        """Class initialization tests"""
        m = self.m
        self.assertIsInstance(m, md.MathDoku)
        self.assertEqual(TEST_GRID_SIZE, m.max_value())

        m.init_puzzle(cages=TEST_CAGES, cage_map=TEST_CAGE_MAP)
        self.assertTrue(m.is_puzzle_valid())

        self.assertEqual(4, m.get(1, 3))
        return

    def test_invalid_cages(self):
        """Test sanity checks on cages"""
        cage_target_too_low = [(0, '+', 2)]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=cage_target_too_low, cage_map=TEST_CAGE_MAP)

        cage_target_too_high = [(TEST_GRID_SIZE * TEST_GRID_SIZE + 1, '*', 2)]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=cage_target_too_high, cage_map=TEST_CAGE_MAP)

        cage_target_too_high = [(TEST_GRID_SIZE + TEST_GRID_SIZE + 1, '+', 2)]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=cage_target_too_high, cage_map=TEST_CAGE_MAP)

        cage_target_too_high = [(TEST_GRID_SIZE, '-', 2)]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=cage_target_too_high, cage_map=TEST_CAGE_MAP)

        cage_target_too_high = [(TEST_GRID_SIZE + 1, '/', 2)]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=cage_target_too_high, cage_map=TEST_CAGE_MAP)
        return

    def test_invalid_cage_map(self):
        """Test sanity checks on cage maps"""
        too_many_cells = [
            [0, 0, 1, 1],
            [2, 0, 1, 1],  # error col 3 (too many assigned to cage 1)
            [2, 3, 4, 4],
            [3, 3, 5, 5],
        ]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=TEST_CAGES, cage_map=too_many_cells)

        too_few_cells = [
            [0, 0, 1, 1],
            [2, 0, 1, 6],
            [2, 4, 4, 4],  # error col 1 (too few assigned to cage 3)
            [3, 3, 5, 5],
        ]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=TEST_CAGES, cage_map=too_few_cells)

        no_such_cage = [
            [0, 0, 1, 1],
            [2, 0, 1, 7],  # error end of row (no such cage)
            [2, 3, 4, 4],
            [3, 3, 5, 5],
        ]
        self.assertRaises(ValueError, self.m.init_puzzle, cages=TEST_CAGES, cage_map=no_such_cage)
        return

    def test_cage_possibilities(self):
        """Test internal helper that calculates possible values for cage"""
        self.m._generate_cage_options()
        for i in range(len(TEST_CAGES)):
            self.assertEqual(TEST_CAGE_POSSIBILITIES[i], self.m._cage_possibilities[i])
        return

    def test_get_allowed_values(self):
        """Test get_allowed_values"""
        self.assertEqual({4}, self.m.get_allowed_values(1, 3))
        self.assertEqual({1, 2}, self.m.get_allowed_values(1, 1))
        self.assertEqual({1, 2, 3}, self.m.get_allowed_values(0, 3))
        return

    def test_solve_puzzle(self):
        """Test that our solution is accepted"""
        for x in range(TEST_GRID_SIZE):
            for y in range(TEST_GRID_SIZE):
                self.m.set(x, y, SOLUTION[x][y])
        self.assertTrue(self.m.is_solved())
        return


if __name__ == "__main__":
    unittest.main()
