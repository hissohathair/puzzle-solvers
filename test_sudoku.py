# test_sudoku.py

import unittest
import puzzlegrid as pg
import sudoku as su
import os


TEST_PUZZLE_STRINGS = [
    # 4x4
    '21...32....41...',
    '42..1....12....3',
    '.2....2.3.4.2..1',

    # 9x9
    '89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13',
]

TEST_SOLUTION_STRINGS = [
    # 9x9
    '893472156146358792275619834954183267782965341361247985518734629639521478427896513',
]

EASY_PUZZLE = pg.from_string("89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13")
EASY_SOLUTION = pg.from_string("893472156146358792275619834954183267782965341361247985518734629639521478427896513")
EASY_MOVES_LEGAL = [[0, 2, 3], [3, 3, 1], [4, 4, 6], [1, 6, 7], [7, 3, 5], [1, 8, 2], [8, 2, 7]]
EASY_MOVES_ILLEGAL = [[0, 2, 8], [0, 2, 1], [3, 3, 2], [3, 3, 4], [2, 2, 4], [3, 3, 6], [0, 0, 9]]

HARD_PUZZLE = pg.from_string("..8......1..6..49.5......7..7..4.....5.2.6...8..79..1..63.....1..5.73......9..75.")
HARD_SOLUTION = pg.from_string("498157632137682495526439178671348529359216847842795316763524981915873264284961753")


class TestSudoku(unittest.TestCase):
    def setUp(self):
        self.p = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_PUZZLE)
        self.s = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_SOLUTION)
        self.legal_moves = EASY_MOVES_LEGAL
        self.illegal_moves = EASY_MOVES_ILLEGAL
        return

    def test_class_init_copies(self):
        """Class init makes a copy of starting grid"""
        x = 0
        y = 2
        new_value = 3
        self.assertTrue(self.p.is_empty(x, y))  # test data error
        self.assertNotEqual(self.p.get(x, y), new_value)  # test data error

        # Change value -- puzzle but not original list should change
        self.p.set(x, y, new_value)
        self.assertEqual(new_value, self.p.get(x, y))
        self.assertNotEqual(new_value, EASY_PUZZLE[x][y])
        return

    def test_class_init_empty(self):
        """Class init can create an empty grid"""
        p = su.SudokuPuzzle()
        for x in range(p.max_value()):
            for y in range(p.max_value()):
                self.assertTrue(p.is_empty(x, y))
        return

    def test_puzzle_sizes(self):
        """Different puzzle sizes are supported"""
        # Initialise all test puzzles, at different sizes
        for i, puzzle in enumerate(TEST_PUZZLE_STRINGS):
            with self.subTest(f"Test Puzzle {i} init (len={len(puzzle)})"):
                p = su.SudokuPuzzle(starting_grid=pg.from_string(puzzle))
                self.assertTrue(p.is_puzzle_valid())
        return

    def test_class_init_raises_exception(self):
        """Class init raises an exception for malformed grids"""
        data = [1, 2, 3]
        self.assertRaises(ValueError, self.p.init_puzzle, data)
        data = [[1, 2, 3] for x in range(self.p.max_value())]
        self.assertRaises(ValueError, self.p.init_puzzle, data)
        return

    def test_box_num_toxy(self):
        """Conversion of box numbers to (x,y) positions

        0 (0,0)   1 (0, 3)   2 (0, 6)
        3 (3,0)   4 (3, 3)   5 (3, 6)
        6 (6,0)   7 (6, 3)   8 (6, 6)
        """
        correct_values = [
            (0, 0),
            (0, 3),
            (0, 6),
            (3, 0),
            (3, 3),
            (3, 6),
            (6, 0),
            (6, 3),
            (6, 6),
        ]
        for i in range(self.p.max_value()):
            with self.subTest(f"Cage {i} at {correct_values[i]}"):
                self.assertEqual(self.p.box_num_to_xy(i), correct_values[i])
                self.assertEqual(self.p.box_xy_to_num(*correct_values[i]), i)
        return

    def test_box_xy_tonum(self):
        """Conversion of x,y cell positions to box numbers"""
        for x in range(self.p.max_value()):
            for y in range(self.p.max_value()):
                with self.subTest(f"Cage for {x},{y}"):
                    num = self.p.box_xy_to_num(x, y)
                    pos = self.p.box_num_to_xy(num)
                    self.assertEqual(
                        self.p.box_xy_to_num(x, y), self.p.box_xy_to_num(*pos)
                    )
        return

    def test_clear_and_set(self):
        """Clear and set a value for a cell"""
        x = 1
        y = 1
        test_value = EASY_PUZZLE[x][y]
        self.assertTrue(test_value)  # test data error

        # Clear op
        num_empty = self.p.num_empty_cells()
        self.p.clear(x, y)
        self.assertTrue(self.p.is_empty(x, y))
        self.assertEqual(num_empty + 1, self.p.num_empty_cells())

        # Set op
        self.p.set(x, y, test_value)
        self.assertEqual(self.p.get(x, y), test_value)
        self.assertFalse(self.p.is_empty(x, y))
        self.assertEqual(num_empty, self.p.num_empty_cells())
        return

    def test_empty_cells(self):
        """Check the methods for getting empty cells"""
        with self.subTest(f"Basic empty cell count check"):
            self.assertEqual(len(self.p.get_all_empty_cells()), 50)
            self.assertEqual(
                len(self.p.get_all_empty_cells()), self.p.num_empty_cells()
            )
            self.assertEqual(len(self.s.get_all_empty_cells()), 0)
            self.assertEqual(
                len(self.s.get_all_empty_cells()), self.s.num_empty_cells()
            )

        with self.subTest(f"Empty cells are empty"):
            for m in self.p.get_all_empty_cells():
                self.assertTrue(self.p.is_empty(*m))
        return

    def test_next_empty_cell(self):
        """Test generator function next_empty_cell()"""
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

    def test_get_values(self):
        """Get row, column, and box values"""
        with self.subTest("get_row_values"):
            self.assertEqual(self.p.get_row_values(0), [8, 9, 4, 5, 6])
            self.assertEqual(self.p.get_row_values(7), [3, 2, 1, 7, 8])

        with self.subTest("get_column_values"):
            self.assertEqual(self.p.get_column_values(0), [8, 1, 9, 4])
            self.assertEqual(self.p.get_column_values(7), [5, 9, 4, 7, 1])

        with self.subTest("get_box_values"):
            self.assertEqual(self.p.get_box_values(0, 0), [8, 9, 1, 4])
            self.assertEqual(self.p.get_box_values(7, 0), [8, 3, 4, 2])
            self.assertEqual(self.p.get_box_values(7, 7), [7, 8, 1, 3])
        return

    def test_possible_values(self):
        """Test that function returns legal values"""
        with self.subTest("Checking possible values"):
            self.assertEqual(self.p.get_allowed_values(0, 0), {8})
            self.assertEqual(self.p.get_allowed_values(2, 2), {2, 3, 5, 6, 7})
            self.assertEqual(self.p.get_allowed_values(7, 0), {5, 6})

        with self.subTest("Possible values are legal"):
            for x in range(self.p.max_value()):
                for y in range(self.p.max_value()):
                    with self.subTest(f"Cell {x},{y}"):
                        vlist = self.p.get_allowed_values(x, y)
                        if self.p.is_empty(x, y):
                            self.assertTrue(len(vlist) >= 1)
                        else:
                            self.assertTrue(len(vlist) == 1)

                        with self.subTest(f"Cell {x},{y} -> {vlist}"):
                            for v in vlist:
                                self.assertTrue(self.p.is_allowed_value(x, y, v))
        return

    def test_legal_move(self):
        """Correctly tell us if a move is legal"""
        for i in range(len(self.legal_moves)):
            with self.subTest(i=i):
                m = self.legal_moves[i]
                self.assertEqual(EASY_SOLUTION[m[0]][m[1]], m[2])  # test data error
                self.assertTrue(self.p.is_allowed_value(*m))
        return

    def test_invalid_move(self):
        """Correctly tell us if we use a value out of range for a cell"""
        self.assertRaises(ValueError, self.p.set, 0, 0, 0)
        self.assertRaises(ValueError, self.p.set, 0, 0, self.p.max_value() + 1)
        return

    def test_illegal_moves(self):
        """Correctly tell us if a move is NOT legal"""
        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = self.illegal_moves[i]
                self.assertFalse(self.p.is_allowed_value(*m))
        return

    def test_illegal_set(self):
        """Throw exception if we attempt an illegal move"""
        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = self.illegal_moves[i]
                self.assertRaises(ValueError, self.p.set, *m)
        return

    def test_is_puzzle_valid(self):
        """Correctly tell us if a puzzle grid is or is not valid"""
        self.assertTrue(self.p.is_puzzle_valid())

        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = list(self.illegal_moves[i])
                new_val = m.pop()
                old_val = self.p.get(*m)
                self.p._grid[m[0]][m[1]] = new_val
                self.assertFalse(self.p.is_puzzle_valid())
                self.p._grid[m[0]][m[1]] = old_val
                self.assertTrue(self.p.is_puzzle_valid())
        return

    def test_is_solved(self):
        """Correctly tell us if a puzzle is solved"""
        self.assertFalse(self.p.is_solved())

        v = self.s.get(0, 0)
        self.s.clear(0, 0)
        self.assertFalse(self.s.is_solved())

        self.s.set(0, 0, v)
        self.assertTrue(self.s.is_solved())
        return

    def test_play_legal_game(self):
        """Plays an entire game consisting of only legal moves"""
        self.assertFalse(self.p.is_solved())  # test data error
        self.assertTrue(self.s.is_solved())

        for m in self.p.get_all_empty_cells():
            self.p.set(*m, self.s.get(*m))
        self.assertTrue(self.p.is_solved())
        return

    def test_play_dodgy_game(self):
        """Plays an entire game, including some illegal moves"""
        self.assertFalse(self.p.is_solved())  # test data error

        # Make some legal moves
        for m in self.legal_moves:
            self.subTest(f"Legal move: {m}")
            self.p.set(*m)
        self.assertTrue(self.p.is_puzzle_valid())

        # Attempt to make some illegal moves
        for m in self.illegal_moves:
            self.subTest(f"Illegal move {m}")
            self.assertTrue(len(m) == 3)
            self.assertFalse(self.p.is_allowed_value(*m))
            self.assertRaises(ValueError, self.p.set, *m)
        self.assertTrue(self.p.is_puzzle_valid())

        # Finish the game
        for m in self.p.get_all_empty_cells():
            v = self.s.get(*m)
            if not self.p.is_allowed_value(*m, v + 1):
                self.assertRaises(ValueError, self.p.set, *m, v + 1)
            self.p.set(*m, v)

        self.assertTrue(self.p.is_solved())
        return

    def test_all_sample_puzzles(self):
        """Loads all the sample puzzles to check for formatting and validity"""
        for puz in su.SAMPLE_PUZZLES:
            with self.subTest(puz["label"]):
                self.p.init_puzzle(pg.from_string(puz["puzzle"]))
                self.assertTrue(self.p.is_puzzle_valid())
        return

    def test_as_string(self):
        """String representations of puzzle grid"""
        self.assertTrue(len(self.p.__str__()) >= 81)
        self.assertTrue(len(self.p.as_html()) > 900)
        self.assertTrue(len(self.p.as_html(show_possibilities=2)) > 950)

        self.assertTrue(len(self.s.__str__()) >= 81)
        self.assertTrue(len(self.s.as_html()) > 900)
        self.assertTrue(len(self.s.as_html(show_possibilities=2)) > 900)
        return


class TestSolver(unittest.TestCase):
    """Test cases for SudokuSolver"""

    def setUp(self):
        """Handy to have an unsolved (p) and already solved puzzle (s) for later tests"""
        self.p = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_PUZZLE)
        self.s = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_SOLUTION)
        return

    def test_backtracking(self):
        """Test the backtracking solution"""
        solver = su.BacktrackingSolver()
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))
        return

    def test_constraing_propogation(self):
        """Test the backtracking + constraint propogation solution"""
        solver = su.ConstraintPropogationSolver()
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))
        return

    def test_single_possibilities(self):
        """The 'easy' puzzle can be solved using single possibilities only"""
        solver = su.DeductiveSolver()
        self.assertTrue(solver.solve_single_possibilities(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))
        return

    def test_only_squares(self):
        """Solve a puzzle using 'only squares' technique"""
        solver = su.DeductiveSolver()

        with self.subTest("Solve some only squares by row"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve_only_row_squares(self.p) > 0)

        with self.subTest("Solve some only squares by column"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve_only_column_squares(self.p) > 0)

        with self.subTest("Solve some only squares by box"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve_only_box_squares(self.p) > 0)

        with self.subTest("Solve using only squares (all)"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve_only_squares(self.p))
            self.assertTrue(self.p.is_solved())
            self.assertEqual(str(self.s), str(self.p))
        return

    def test_two_out_of_three(self):
        """Test the "2 out of 3" strategy"""
        solver = su.DeductiveSolver()
        num_empty = self.p.num_empty_cells()

        # This one can't actually solve the first puzzle, but can solve a
        # few cells
        solver.solve_two_out_of_three(self.p)
        self.assertTrue(self.p.num_empty_cells() < num_empty)
        return

    def test_deductive(self):
        """Test all deductives as a single class"""
        with self.subTest("DeductiveSolver without backtracking"):
            solver = su.DeductiveSolver(use_backtracking=False)

            # Deductive without backtracking can solve EASY_PUZZLE
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve(self.p))
            self.assertTrue(self.p.is_solved())

            # Deductive without backtracking can NOT solve hard puzzle
            self.p.init_puzzle(HARD_PUZZLE)
            self.assertFalse(solver.solve(self.p))
            self.assertFalse(self.p.is_solved())

        with self.subTest("DeductiveSolver with backtracking"):
            solver = su.DeductiveSolver(use_backtracking=True)

            # Deductive with backtracking can solve hard puzzle
            self.p.init_puzzle(HARD_PUZZLE)
            self.assertTrue(solver.solve(self.p))
            self.assertTrue(self.p.is_solved())
        return

    def test_sat(self):
        """Test the Boolean SAT solver"""
        solver = su.SATSolver()

        # Correct clauses?
        mv = self.p.max_value()
        mp = mv - 1
        every_cell_has_a_value = (mv ** 2)
        no_cell_has_two_values = (mp ** 2 + mp) // 2
        num_regions = mv * 3
        regions_have_unique_values = no_cell_has_two_values * mv

        # Assuming test puzzle is 9x9
        assert len(str(self.p)) == 81  # test data error
        assert every_cell_has_a_value == 81
        assert no_cell_has_two_values == 36
        assert num_regions == 27
        assert regions_have_unique_values == 324

        expected_clauses = every_cell_has_a_value * (1 + no_cell_has_two_values) + num_regions * regions_have_unique_values
        assert expected_clauses == 11745

        # Every puzzle clue counts for an additional clause
        num_clues = self.p.num_cells() - self.p.num_empty_cells()
        expected_clauses += num_clues

        # Check that we generate correct number of clauses
        self.assertEqual(expected_clauses, len(solver.get_sat_clauses(self.p)))

        # Can solve?
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))
        return

    def test_solver(self):
        """SudokuSolver can be vaguely useful"""
        with self.subTest("Default solver works"):
            solver = su.SudokuSolver()
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve(self.p))

            self.p.init_puzzle(HARD_PUZZLE)
            self.assertTrue(solver.solve(self.p))

        with self.subTest("Bad solver raises exception"):
            self.assertRaises(ValueError, su.SudokuSolver, method="banana")
        return

    def test_all_solvers(self):
        """Test that all available solvers are supported"""
        for x in su.SOLVERS:
            with self.subTest(f"Method {x}"):
                solver = su.SudokuSolver(method=x)
                self.p.init_puzzle(EASY_PUZZLE)
                self.assertTrue(solver.solve(self.p))
                self.assertTrue(self.p.is_solved())

                self.p.init_puzzle(HARD_PUZZLE)
                self.assertTrue(solver.solve(self.p))
                self.assertTrue(self.p.is_solved())
        return

    @unittest.skipUnless(os.environ.get('SUDOKU_LONG_TESTS', False), 'Long running test')
    def test_all_solvers_all_puzzles(self):
        """Test that all available solvers can solve all test puzzles in sudoku.py"""
        for x in su.SOLVERS:
            if x == 'backtracking':
                continue
            solver = su.SudokuSolver(method=x)
            for p in su.SAMPLE_PUZZLES:
                with self.subTest(f"Method {x} on puzzle {p['label']}"):
                    puzzle = su.SudokuPuzzle(starting_grid=pg.from_string(p['puzzle']))
                    self.assertTrue(solver.solve(puzzle))
                    self.assertTrue(puzzle.is_solved())
        return


class TestPuzzleTester(unittest.TestCase):
    def setUp(self):
        self.include_levels = ['Kids', 'Easy', 'Moderate', 'Hard']
        self.test_cases = [x for x in su.SAMPLE_PUZZLES if x['level'] in self.include_levels]
        self.pt = pg.PuzzleTester(puzzle_class=su.SudokuPuzzle)
        self.pt.add_testcases(self.test_cases)
        return

    def test_solver(self):
        """Use PuzzleTester class to test SudokuSolver"""
        for ac in [False, True]:
            for m in su.SOLVERS:
                with self.subTest(f"method: {m}; anti-cheat: {ac}"):
                    self.pt.anti_cheat_checking = ac
                    s = su.SudokuSolver(method=m)
                    self.assertEqual(8, self.pt.num_testcases())
                    self.assertEqual(8, self.pt.run_tests(s, m))
        return

    def callback(self, a, b, c, d, e):
        self._callback_called = True
        return

    def test_callback(self):
        """Test that callback is called"""
        self._callback_called = False
        s = su.SudokuSolver()
        self.pt.run_tests(s, 'default', callback=self.callback)
        self.assertTrue(self._callback_called)
        return

    def test_results(self):
        """Check test results"""
        s = su.SudokuSolver()
        self.assertEqual(3, len(self.pt.get_test_results()))
        self.pt.run_tests(s, 'default')
        self.assertEqual(4, len(self.pt.get_test_results()))
        self.assertEqual(1, len(self.pt.get_test_labels()))
        self.assertEqual({'default'}, self.pt.get_test_labels())

        tr = self.pt.get_test_results()
        newpt = pg.PuzzleTester(puzzle_class=su.SudokuPuzzle)
        newpt.set_test_results(tr)
        self.assertEqual(self.pt.get_test_results(), newpt.get_test_results())
        return


if __name__ == "__main__":
    unittest.main()
