# test_puzzlegrid.py

import unittest
import puzzlegrid as pg

DEFAULT_PUZZLE_SIZE = 9
TEST_PUZZLE = [
    [8, 9, 0, 4, 0, 0, 0, 5, 6],
    [1, 4, 0, 3, 5, 0, 0, 9, 0],
    [0, 0, 0, 0, 0, 0, 8, 0, 0],
    [9, 0, 0, 0, 0, 0, 2, 0, 0],
    [0, 8, 0, 9, 6, 5, 0, 4, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 5],
    [0, 0, 8, 0, 0, 0, 0, 0, 0],
    [0, 3, 0, 0, 2, 1, 0, 7, 8],
    [4, 2, 0, 0, 0, 6, 0, 1, 3],
]

SOLVED_PUZZLE = [
    [8, 9, 3, 4, 7, 2, 1, 5, 6],
    [1, 4, 6, 3, 5, 8, 7, 9, 2],
    [2, 7, 5, 6, 1, 9, 8, 3, 4],
    [9, 5, 4, 1, 8, 3, 2, 6, 7],
    [7, 8, 2, 9, 6, 5, 3, 4, 1],
    [3, 6, 1, 2, 4, 7, 9, 8, 5],
    [5, 1, 8, 7, 3, 4, 6, 2, 9],
    [6, 3, 9, 5, 2, 1, 4, 7, 8],
    [4, 2, 7, 8, 9, 6, 5, 1, 3],
]


class TestPuzzleGrid(unittest.TestCase):
    def setUp(self):
        """
        We (almost) always need these
        """
        self.p = pg.ConstraintPuzzle()
        return

    def test_class_init(self):
        """
        Test class initialization
        """
        with self.subTest("Defaults"):
            # Has correct dimensions
            p = pg.ConstraintPuzzle()
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_empty_cells())
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_cells())
            self.assertEqual(set(range(1, DEFAULT_PUZZLE_SIZE + 1)), p._complete_set)
            self.assertEqual(DEFAULT_PUZZLE_SIZE, p.max_value())

            # Is empty by default
            for x in range(DEFAULT_PUZZLE_SIZE):
                for y in range(DEFAULT_PUZZLE_SIZE):
                    self.assertTrue(p.is_empty(x, y))

        for i in range(pg.MIN_PUZZLE_SIZE, pg.MAX_PUZZLE_SIZE + 1):
            with self.subTest(f"Puzzle size = {i}"):
                p = pg.ConstraintPuzzle(grid_size=i)
                self.assertEqual(i * i, p.num_empty_cells())
                self.assertEqual(i * i, p.num_cells())
                self.assertEqual(set(range(1, i + 1)), p._complete_set)

        with self.subTest("Out of range grids"):
            self.assertRaises(ValueError, pg.ConstraintPuzzle, 0)
            self.assertRaises(ValueError, pg.ConstraintPuzzle, 26)
        return

    def test_get_set_and_clear(self):
        """
        Correctly get, set and clear value
        """
        # Setting some values along the top row
        row = 0
        with self.subTest(f"Testing row {row}"):
            for i in range(DEFAULT_PUZZLE_SIZE):
                self.assertTrue(self.p.is_empty(row, i))
                self.p.set(row, i, i + 1)
                self.assertEqual(i + 1, self.p.get(row, i))
            self.assertEqual(
                DEFAULT_PUZZLE_SIZE ** 2 - DEFAULT_PUZZLE_SIZE, self.p.num_empty_cells()
            )

            for i in range(DEFAULT_PUZZLE_SIZE):
                self.assertFalse(self.p.is_empty(row, i))
                self.p.clear(row, i)
                self.assertTrue(self.p.is_empty(row, i))
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_empty_cells())

        # Setting some values down column
        col = 1
        with self.subTest(f"Testing column {col}"):
            for i in range(DEFAULT_PUZZLE_SIZE):
                self.assertTrue(self.p.is_empty(i, col))
                self.p.set(i, col, i + 1)
                self.assertEqual(i + 1, self.p.get(i, col))
            self.assertEqual(
                DEFAULT_PUZZLE_SIZE ** 2 - DEFAULT_PUZZLE_SIZE, self.p.num_empty_cells()
            )

            for i in range(DEFAULT_PUZZLE_SIZE):
                self.assertFalse(self.p.is_empty(i, col))
                self.p.clear(i, col)
                self.assertTrue(self.p.is_empty(i, col))
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_empty_cells())

        return

    def test_allowed_values(self):
        """
        Test that is_allowed_value correctly enforces constraints
        """
        row = 2
        col = 2
        val = 2
        self.p.set(row, col, val)

        self.assertTrue(self.p.is_allowed_value(row, col, val))
        self.assertTrue(self.p.is_allowed_value(row + 1, col + 1, val))
        self.assertFalse(self.p.is_allowed_value(row, col + 1, val))
        self.assertFalse(self.p.is_allowed_value(row + 1, col, val))
        return

    def test_init_puzzle(self):
        """
        Load a Sudoku grid
        """
        with self.subTest("Using test puzzle"):
            self.p.init_puzzle(TEST_PUZZLE)
            self.assertEqual(50, self.p.num_empty_cells())
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_cells())
            self.assertTrue(self.p.is_puzzle_valid())
            self.assertFalse(self.p.is_solved())

        with self.subTest("Using solved puzzle"):
            self.p.init_puzzle(SOLVED_PUZZLE)
            self.assertEqual(0, self.p.num_empty_cells())
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_cells())
            self.assertTrue(self.p.is_puzzle_valid())
            self.assertTrue(self.p.is_solved())
        return

    def test_as_string(self):
        """
        Just test that we get some kind of string.
        """
        self.assertTrue(len(self.p.__str__()) > 160)
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertTrue(len(self.p.__str__()) > 160)
        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertTrue(len(self.p.__str__()) > 160)


if __name__ == "__main__":
    unittest.main()
