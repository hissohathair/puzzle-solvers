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
        """Test build_empty_grid"""
        for i in range(pg.MIN_PUZZLE_SIZE, pg.MAX_PUZZLE_SIZE):
            x = pg.build_empty_grid(i)
            self.assertEqual(len(x), i)
        return

    def test_char2int(self):
        """Test conversion of ints to chars and back"""
        test_pairs = [
            (1, '1'), (2, '2'), (9, '9'), (10, 'A'), (11, 'B'),
            (25, 'P'), (pg.EMPTY_CELL, '.')
        ]
        for tp in test_pairs:
            i, c = tp
            with self.subTest(f"{i} == {c}"):
                self.assertEqual(i, pg.char2int(c))
                self.assertEqual(c, pg.int2char(i))

        # Full range
        with self.subTest(f"Range 0..{pg.MAX_PUZZLE_SIZE}"):
            for i in range(pg.MAX_PUZZLE_SIZE):
                self.assertEqual(pg.int2char(i), pg.int2char(pg.char2int(pg.int2char(i))))

        return

    def test_count_clues(self):
        """Count the number of clues in a starting puzzle"""
        self.assertEqual(31, pg.count_clues(TEST_PUZZLE))
        self.assertEqual(31, pg.count_clues(TEST_STRING))
        self.assertEqual(81, pg.count_clues(SOLVED_PUZZLE))
        self.assertEqual(81, pg.count_clues(SOLVED_STRING))
        return

    def test_has_same_clues(self):
        """We can verify a solution is derived from a puzzle"""
        puzzle = pg.ConstraintPuzzle(starting_grid=TEST_PUZZLE)
        solution = pg.ConstraintPuzzle(starting_grid=SOLVED_PUZZLE)
        self.assertTrue(pg.has_same_clues(puzzle, solution))
        self.assertFalse(pg.has_same_clues(solution, puzzle))

        empty_puzzle = pg.ConstraintPuzzle(grid_size=pg.DEFAULT_PUZZLE_SIZE)
        self.assertTrue(pg.has_same_clues(empty_puzzle, puzzle))
        self.assertFalse(pg.has_same_clues(puzzle, empty_puzzle))

        small_puzzle = pg.ConstraintPuzzle(grid_size=pg.DEFAULT_PUZZLE_SIZE - 1)
        self.assertFalse(pg.has_same_clues(empty_puzzle, small_puzzle))
        return

    def test_from_string(self):
        """Convert strings to 2D arrays with useful error messages"""
        with self.subTest("Properly formed strings working"):
            self.assertEqual(SOLVED_PUZZLE, pg.from_string(SOLVED_STRING))
            self.assertEqual([[None]], pg.from_string('.'))
            self.assertEqual([[1]], pg.from_string('1'))

        for i in [1, 4, 9, 16, 25]:
            with self.subTest(f"String length {i}"):
                self.assertEqual(pg.build_empty_grid(i), pg.from_string('.' * i ** 2))

        with self.subTest("Badly formed strings raise exception"):
            self.assertRaises(ValueError, pg.from_string, TEST_STRING[0:-1])
            self.assertRaises(ValueError, pg.from_string, '.' * (25 ** 2 - 1))
            self.assertRaises(ValueError, pg.from_string, '2')
            self.assertRaises(ValueError, pg.from_string, '1223')
            self.assertRaises(ValueError, pg.from_string, '')
        return


class TestPuzzleGrid(unittest.TestCase):
    def setUp(self):
        self.p = pg.ConstraintPuzzle()
        return

    def test_class_init(self):
        """Test class initialization"""

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

        with self.subTest("grid_size and starting_grid disagree"):
            self.assertRaises(ValueError, pg.ConstraintPuzzle, grid_size=8, starting_grid=TEST_PUZZLE)
        return

    def test_set(self):
        """Correctly set values"""
        self.p.set(1, 1, 1)
        self.assertEqual(1, self.p.get(1, 1))

        # Can over-write already set cell
        self.p.set(1, 1, 1)
        self.assertEqual(1, self.p.get(1, 1))
        return

    def test_get_set_and_clear(self):
        """Correctly get, set and clear value"""

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

    def test_find_empty_cell(self):
        """Finds first available empty cell"""
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertEqual((0, 2), self.p.find_empty_cell())

        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertEqual((), self.p.find_empty_cell())
        return

    def test_all_empty_cells(self):
        """Check the methods for getting empty cells"""
        with self.subTest(f"Basic empty cell count check"):
            self.p.init_puzzle(TEST_PUZZLE)
            self.assertEqual(50, len(self.p.get_all_empty_cells()))
            self.assertEqual(50, self.p.num_empty_cells())

            self.p.init_puzzle(SOLVED_PUZZLE)
            self.assertEqual(0, len(self.p.get_all_empty_cells()))
            self.assertEqual(0, self.p.num_empty_cells())

        with self.subTest(f"Empty cells are empty"):
            self.p.init_puzzle(TEST_PUZZLE)
            for m in self.p.get_all_empty_cells():
                self.assertTrue(self.p.is_empty(*m))
        return

    def test_next_empty_cell(self):
        """Test generator function next_empty_cell()"""
        self.p.init_puzzle(TEST_PUZZLE)
        with self.subTest(f"next_empty_cell returns all empty cells"):
            mts = [m for m in self.p.next_empty_cell()]
            self.assertEqual(mts, self.p.get_all_empty_cells())

        with self.subTest(f"next_empty_cell terminates"):
            i = 0
            for m in self.p.next_empty_cell():
                i += 1
            self.assertEqual(i, 50)

        with self.subTest(f"next_empty_cell can get one cell at a time"):
            mts = self.p.get_all_empty_cells()
            self.assertEqual(len(mts), 50)

            mtGen = self.p.next_empty_cell()
            for m in mts:
                x = next(mtGen)
                self.assertEqual(m, x)
        return

    def test_allowed_values(self):
        """Test that is_allowed_value correctly enforces constraints"""
        row = 2
        col = 2
        val = 2
        self.p.set(row, col, val)
        self.assertEqual(val, self.p.get(row, col))
        self.assertEqual({val}, self.p.get_allowed_values(row, col))

        self.assertTrue(self.p.is_allowed_value(row, col, val))
        self.assertTrue(self.p.is_allowed_value(row + 1, col + 1, val))
        self.assertFalse(self.p.is_allowed_value(row, col + 1, val))
        self.assertFalse(self.p.is_allowed_value(row + 1, col, val))
        return

    def test_init_puzzle(self):
        """Load a Sudoku grid"""

        with self.subTest("Using unsolved puzzles"):
            for i in [TEST_PUZZLE, pg.from_string(TEST_STRING)]:
                # Init existing puzzle instance
                self.p.init_puzzle(i)
                self.assertEqual(50, self.p.num_empty_cells())
                self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_cells())
                self.assertTrue(self.p.is_puzzle_valid())
                self.assertFalse(self.p.is_solved())

                # Init on creation
                p = pg.ConstraintPuzzle(starting_grid=i)
                self.assertEqual(50, p.num_empty_cells())
                self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_cells())
                self.assertTrue(p.is_puzzle_valid())
                self.assertFalse(p.is_solved())

        with self.subTest("Using solved puzzles"):
            for i in [SOLVED_PUZZLE, pg.from_string(SOLVED_STRING)]:
                # Init existing puzzle instance
                self.p.init_puzzle(i)
                self.assertEqual(0, self.p.num_empty_cells())
                self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, self.p.num_cells())
                self.assertTrue(self.p.is_puzzle_valid())
                self.assertTrue(self.p.is_solved())

                # Init on creation
                p = pg.ConstraintPuzzle(starting_grid=i)
                self.assertEqual(0, p.num_empty_cells())
                self.assertEqual(DEFAULT_PUZZLE_SIZE ** 2, p.num_cells())
                self.assertTrue(p.is_puzzle_valid())
                self.assertTrue(p.is_solved())

        with self.subTest("Bad puzzle init"):
            for i in [TEST_STRING, pg.from_string(SOLVED_STRING)]:
                self.assertRaises(ValueError, self.p.init_puzzle, i[0:-1])

        return

    def test_as_string(self):
        """
        Just test that we get some kind of string.
        """
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertEqual(TEST_STRING, str(self.p))
        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertEqual(SOLVED_STRING, str(self.p))

    def test_is_solved(self):
        """Check that is_solved is not so easily fooled"""
        self.p.init_puzzle(TEST_PUZZLE)
        self.assertFalse(self.p.is_solved())

        self.p.init_puzzle(SOLVED_PUZZLE)
        self.assertTrue(self.p.is_solved())

        self.p.init_puzzle(TEST_PUZZLE)
        self.p._num_empty_cells = 0
        self.assertFalse(self.p.is_solved())

        self.p.init_puzzle(SOLVED_PUZZLE)
        self.p._grid[0][0] = self.p._grid[0][1]
        self.assertFalse(self.p.is_solved())
        return

    def test_strings(self):
        """String representations of puzzles"""
        self.assertEqual(self.p.num_cells(), len(str(self.p)))
        self.assertEqual(self.p.num_cells() * 2 - 1, len(self.p.as_grid()))
        return


class TestSolver(unittest.TestCase):
    def test_class_init(self):
        """Test that class initializes"""
        p = pg.ConstraintPuzzle(starting_grid=pg.from_string(TEST_STRING))
        s = pg.ConstraintSolver()
        self.assertRaises(NotImplementedError, s.solve, p)
        return


class TestPuzzleTester(unittest.TestCase):
    """Tests for the class PuzzleTester"""

    def setUp(self):
        """Repeatedly used test fixtures"""
        self.pt = pg.PuzzleTester()
        self.s = pg.ConstraintSolver()
        self.tc = [
            {'label': 'test puzzle grid', 'puzzle': TEST_PUZZLE},
            {'label': 'test puzzle string', 'puzzle': TEST_STRING},
            {'label': 'solved puzzle grid', 'puzzle': SOLVED_PUZZLE},
            {'label': 'solved puzzle string', 'puzzle': SOLVED_STRING},
        ]

        return

    def test_class_init(self):
        """Test we can create class"""
        pt = pg.PuzzleTester()
        self.assertTrue(isinstance(pt, pg.PuzzleTester))

    def test_add_cases(self):
        """
        Add some test cases OK. We can't test running it because the solver
        is an abstract base class
        """
        self.pt.add_testcases(self.tc)
        self.assertEqual(4, self.pt.num_testcases())

        # Add some bad cases
        self.assertRaises(ValueError, self.pt.add_testcases, 'banana')
        self.assertRaises(ValueError, self.pt.add_testcases, ['banana', 'vodka'])

        # Add test cases without labels
        self.pt = pg.PuzzleTester()
        for tc in self.tc:
            del tc['label']
        self.pt.add_testcases(self.tc)
        self.assertEqual(4, self.pt.num_testcases())
        return

    def test_from_file(self):
        """test from_file func"""
        tc = pg.from_file("data/sudoku_9x9/hardest.txt")
        self.pt.add_testcases(tc)
        self.assertEqual(13, self.pt.num_testcases())
        return


if __name__ == "__main__":
    unittest.main()
