"""Unit tests for puzzle.latinsquare classes and functions."""

import unittest
import puzzle.latinsquare as ls

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
TEST_STRING = '89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13'

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
SOLVED_STRING = '893472156146358792275619834954183267782965341361247985518734629639521478427896513'


class TestFunctions(unittest.TestCase):
    """Test the helper functions / utilities"""

    def test_build_grid(self):
        """build_empty_grid can build all allowed puzzle sizes"""
        for i in range(ls.MIN_PUZZLE_SIZE, ls.MAX_PUZZLE_SIZE):
            with self.subTest(f"grid size {i}x{i}"):
                grid = ls.build_empty_grid(i)
                self.assertEqual(len(grid), i)

    def test_char2int(self):
        """char2int and int2char converts cell values between numbers and chars"""
        test_pairs = [
            (1, '1'), (2, '2'), (9, '9'), (10, 'A'), (11, 'B'),
            (25, 'P'), (ls.EMPTY_CELL, '.')
        ]
        for tp in test_pairs:
            i, c = tp
            with self.subTest(f"{i} == {c}"):
                self.assertEqual(i, ls.char2int(c))
                self.assertEqual(c, ls.int2char(i))

        # Full range
        with self.subTest(f"Range 0..{ls.MAX_PUZZLE_SIZE}"):
            for i in range(ls.MAX_PUZZLE_SIZE):
                self.assertEqual(ls.int2char(i), ls.int2char(ls.char2int(ls.int2char(i))))

    def test_count_clues(self):
        """count_clues can count the number of clues in string or list format"""
        self.assertEqual(31, ls.count_clues(TEST_PUZZLE))
        self.assertEqual(31, ls.count_clues(TEST_STRING))
        self.assertEqual(81, ls.count_clues(SOLVED_PUZZLE))
        self.assertEqual(81, ls.count_clues(SOLVED_STRING))

    def test_from_string(self):
        """Convert strings to 2D arrays with useful error messages"""
        with self.subTest("Properly formed strings working"):
            self.assertEqual(SOLVED_PUZZLE, ls.from_string(SOLVED_STRING))
            self.assertEqual([[None]], ls.from_string('.'))
            self.assertEqual([[1]], ls.from_string('1'))

        for i in [1, 4, 9, 16, 25]:
            with self.subTest(f"String length {i}"):
                self.assertEqual(ls.build_empty_grid(i), ls.from_string('.' * i ** 2))

        with self.subTest("Badly formed strings raise exception"):
            self.assertRaises(ValueError, ls.from_string, TEST_STRING[0:-1])
            self.assertRaises(ValueError, ls.from_string, '.' * (25 ** 2 - 1))
            self.assertRaises(ValueError, ls.from_string, '2')
            self.assertRaises(ValueError, ls.from_string, '1223')
            self.assertRaises(ValueError, ls.from_string, '')


class TestLatinSquare(unittest.TestCase):
    """Tests for LatinSquare class"""

    def setUp(self):
        self.p = ls.LatinSquare()
        return

    def test_class_init(self):
        """Class initialization at different sizes"""

        # Has correct dimensions with default settings
        with self.subTest("Defaults"):
            p = ls.LatinSquare()
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_empty_cells())
            self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_cells)
            self.assertEqual(set(range(1, DEFAULT_PUZZLE_SIZE + 1)), p.complete_set)
            self.assertEqual(DEFAULT_PUZZLE_SIZE, p.max_value)

            # Is empty by default
            for x in range(p.max_value):
                for y in range(p.max_value):
                    self.assertTrue(p.is_empty(x, y))

        # All sizes can be created within range
        for i in range(ls.MIN_PUZZLE_SIZE, ls.MAX_PUZZLE_SIZE + 1):
            with self.subTest(f"Puzzle size = {i}"):
                p = ls.LatinSquare(grid_size=i)
                self.assertEqual(i * i, p.num_empty_cells())
                self.assertEqual(i * i, p.num_cells)
                self.assertEqual(set(range(1, i + 1)), p.complete_set)

        # Out of range sizes raise errors
        with self.subTest("Out of range grids"):
            self.assertRaises(ValueError, ls.LatinSquare, 0)
            self.assertRaises(ValueError, ls.LatinSquare, ls.MAX_PUZZLE_SIZE + 1)

        # Contradictory arguments raise errors
        with self.subTest("grid_size and starting_grid disagree"):
            self.assertRaises(ValueError, ls.LatinSquare, grid_size=8, starting_grid=TEST_PUZZLE)

    def test_set(self):
        """Correctly set values and have rules enforced"""
        self.p.set(1, 1, 1)
        self.assertEqual(1, self.p.get(1, 1))

        # Can over-write already set cell
        self.p.set(1, 1, 1)
        self.assertEqual(1, self.p.get(1, 1))

        # Can't write same value to same row or column twice
        self.assertRaises(ValueError, self.p.set, 1, 2, 1)
        self.assertRaises(ValueError, self.p.set, 2, 1, 1)

    def test_get_set_and_clear(self):
        """Correctly get, set and clear value"""

        # Setting some values along the top row
        row = 0
        with self.subTest(f"Testing row {row}"):
            for i in range(self.p.max_value):
                self.assertTrue(self.p.is_empty(row, i))
                self.p.set(row, i, i + 1)
                self.assertEqual(i + 1, self.p.get(row, i))
            self.assertEqual(self.p.num_cells - self.p.max_value, self.p.num_empty_cells())

            for i in range(self.p.max_value):
                self.assertFalse(self.p.is_empty(row, i))
                self.p.clear(row, i)
                self.assertTrue(self.p.is_empty(row, i))
            self.assertEqual(self.p.num_cells, self.p.num_empty_cells())

        # Setting some values down column
        col = 1
        with self.subTest(f"Testing column {col}"):
            for i in range(self.p.max_value):
                self.assertTrue(self.p.is_empty(i, col))
                self.p.set(i, col, i + 1)
                self.assertEqual(i + 1, self.p.get(i, col))
            self.assertEqual(self.p.num_cells - self.p.max_value, self.p.num_empty_cells())

            for i in range(self.p.max_value):
                self.assertFalse(self.p.is_empty(i, col))
                self.p.clear(i, col)
                self.assertTrue(self.p.is_empty(i, col))
            self.assertEqual(self.p.num_cells, self.p.num_empty_cells())

    def test_find_empty_cell(self):
        """Finds first available empty cell"""
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertEqual((0, 2), self.p.find_empty_cell())

        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertEqual((), self.p.find_empty_cell())

    def test_fetching_empty_cells(self):
        """Check the methods for getting empty cells"""
        self.p.init_puzzle(TEST_PUZZLE)
        all_empties = [m for m in self.p.next_empty_cell()]
        self.assertEqual(50, len(all_empties))
        self.assertEqual(50, self.p.num_empty_cells())

        self.p.init_puzzle(SOLVED_PUZZLE)
        all_empties = [m for m in self.p.next_empty_cell()]
        self.assertEqual(0, len(all_empties))
        self.assertEqual(0, self.p.num_empty_cells())

    def test_allowed_values(self):
        """Test that is_allowed_value correctly enforces constraints"""
        test_cell = (2, 2)
        next_cell = (3, 3)
        test_value = 2
        self.p.set(*test_cell, test_value)
        self.assertEqual({test_value}, self.p.get_allowed_values(*test_cell))

        self.assertTrue(test_value in self.p.get_allowed_values(*test_cell))
        self.assertTrue(test_value in self.p.get_allowed_values(*next_cell))
        self.assertFalse(test_value in self.p.get_allowed_values(test_cell[0] + 1, test_cell[1]))
        self.assertFalse(test_value in self.p.get_allowed_values(test_cell[0], test_cell[1] + 1))

    def test_init_puzzle(self):
        """Initialize puzzle with starting clues"""

        with self.subTest("Using unsolved puzzles"):
            for i in [TEST_PUZZLE, ls.from_string(TEST_STRING)]:
                # Init existing puzzle instance
                self.p.init_puzzle(i)
                self.assertEqual(50, self.p.num_empty_cells())
                self.assertEqual(self.p.max_value ** 2, self.p.num_cells)
                self.assertTrue(self.p.is_valid())
                self.assertFalse(self.p.is_solved())

                # Init on creation
                newp = ls.LatinSquare(starting_grid=i)
                self.assertEqual(50, newp.num_empty_cells())
                self.assertEqual(self.p.max_value ** 2, newp.num_cells)
                self.assertTrue(newp.is_valid())
                self.assertFalse(newp.is_solved())

        with self.subTest("Using solved puzzles"):
            for i in [SOLVED_PUZZLE, ls.from_string(SOLVED_STRING)]:
                # Init existing puzzle instance
                self.p.init_puzzle(i)
                self.assertEqual(0, self.p.num_empty_cells())
                self.assertEqual(self.p.max_value ** 2, self.p.num_cells)
                self.assertTrue(self.p.is_valid())
                self.assertTrue(self.p.is_solved())

                # Init on creation
                newp = ls.LatinSquare(starting_grid=i)
                self.assertEqual(0, newp.num_empty_cells())
                self.assertEqual(newp.max_value ** 2, newp.num_cells)
                self.assertTrue(newp.is_valid())
                self.assertTrue(newp.is_solved())

        with self.subTest("Bad puzzle init"):
            for i in [TEST_STRING, ls.from_string(SOLVED_STRING)]:
                self.assertRaises(ValueError, self.p.init_puzzle, i[0:-1])

    def test_as_string(self):
        """str and repr representations"""
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertTrue(len(str(self.p)) > 81)
        self.assertEqual(f"LatinSquare(9, '{TEST_STRING}')", repr(self.p))

        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertTrue(len(str(self.p)) > 81)
        self.assertEqual(f"LatinSquare(9, '{SOLVED_STRING}')", repr(self.p))


if __name__ == "__main__":
    unittest.main()
