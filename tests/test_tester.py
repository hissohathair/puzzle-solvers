"""Unit tests for puzzle.tester classes and functions."""

import unittest

import puzzle.latinsquare as ls
import puzzle.sudoku as su

import puzzle.tester as pt


TEST_PUZZLE_STRINGS = [
    "89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13",
    "..75.....1....98...6..1.43.8.5..2.1.......2...1.7....9..3..8..4.4.9..3..9....6.2.",
    "..8......1..6..49.5......7..7..4.....5.2.6...8..79..1..63.....1..5.73......9..75.",
]

SOLVED_PUZZLE_STRINGS = [
    "893472156146358792275619834954183267782965341361247985518734629639521478427896513",
    "387524961124639875569817432835492617796185243412763589673258194248971356951346728",
    "498157632137682495526439178671348529359216847842795316763524981915873264284961753",
]


class TestFunctions(unittest.TestCase):
    """Test the helper functions / utilities"""

    def test_has_same_clues(self):
        """We can verify a solution is derived from a puzzle"""
        for i, puz in enumerate(TEST_PUZZLE_STRINGS):
            pzzl = ls.LatinSquare(starting_grid=ls.from_string(puz))
            soln = ls.LatinSquare(starting_grid=ls.from_string(SOLVED_PUZZLE_STRINGS[i]))
            self.assertTrue(pt.has_same_clues(pzzl, soln))
            self.assertFalse(pt.has_same_clues(soln, pzzl))

        # Can handle empty puzzles
        empty_puzzle = ls.LatinSquare(grid_size=ls.DEFAULT_PUZZLE_SIZE)
        self.assertTrue(pt.has_same_clues(empty_puzzle, pzzl))
        self.assertFalse(pt.has_same_clues(pzzl, empty_puzzle))

        # Can handle mismatched sizes
        small_puzzle = ls.LatinSquare(grid_size=ls.DEFAULT_PUZZLE_SIZE - 1)
        self.assertFalse(pt.has_same_clues(empty_puzzle, small_puzzle))

    def test_from_file(self):
        """Can load test data from file"""
        tester = pt.PuzzleTester(ls.LatinSquare)
        tester.add_test_cases(pt.from_file("data/sudoku_9x9/hardest.txt"))
        self.assertEqual(13, tester.num_test_cases())


class TestPuzzleTester(unittest.TestCase):
    """Tests for the class PuzzleTester using LatinSquare puzzles"""

    def setUp(self):
        self.pt = pt.PuzzleTester(ls.LatinSquare)
        self.test_cases = []

        for i, puz in enumerate(TEST_PUZZLE_STRINGS):
            self.test_cases.append({'label': f"test {i}", 'puzzle': puz})

    def test_class_init_and_add_cases(self):
        """Test we can create class and add test cases"""
        self.assertTrue(isinstance(self.pt, pt.PuzzleTester))

        self.pt.add_test_cases(self.test_cases)
        self.assertEqual(3, self.pt.num_test_cases())

        # Add some bad cases
        self.assertRaises(ValueError, self.pt.add_test_cases, 'banana')
        self.assertRaises(ValueError, self.pt.add_test_cases, ['banana', 'vodka'])

        # Add test cases without labels
        self.pt = pt.PuzzleTester(ls.LatinSquare)
        for tc in self.test_cases:
            del tc['label']
        self.pt.add_test_cases(self.test_cases)
        self.assertEqual(3, self.pt.num_test_cases())

    def test_class_repr(self):
        """Class can represent itself"""
        expected = "PuzzleTester(LatinSquare, test_samples=1, anti_cheat_check=True, num_test_cases=0, solver_labels=set())"
        self.assertEqual(expected, repr(self.pt))


class TestSudokuTester(unittest.TestCase):
    """Tests for the class PuzzleTester using Sudoku puzzles"""

    def setUp(self):
        self.include_levels = ['Kids', 'Easy', 'Moderate']
        self.test_cases = [x for x in su.SAMPLE_PUZZLES if x['level'] in self.include_levels]
        self.pt = pt.PuzzleTester(puzzle_class=su.SudokuPuzzle)
        self.pt.add_test_cases(self.test_cases)

    def test_solver(self):
        """Use PuzzleTester class to test SudokuSolver"""
        for method in su.SOLVERS:
            with self.subTest(f"method: {method}"):
                solver = su.SudokuSolver(method=method)
                self.assertEqual(5, self.pt.num_test_cases())
                self.assertEqual(5, self.pt.run_tests(solver))

    def callback(self, a, b, c, d, e):
        self._callback_called = True
        self._callback_params = (a, b, c, d, e)

    def test_callback(self):
        """Test that callback is called...back"""
        self._callback_called = False
        solver = su.SudokuSolver()
        self.pt.run_tests(solver, callback=self.callback)
        self.assertTrue(self._callback_called)

    def test_results(self):
        """Check test results"""
        solver = su.SudokuSolver()
        self.assertEqual(3, len(self.pt.get_test_results()))
        self.pt.run_tests(solver)
        self.assertEqual(4, len(self.pt.get_test_results()))
        self.assertEqual(1, len(self.pt.get_solver_labels()))

        results = self.pt.get_test_results()
        newpt = pt.PuzzleTester(puzzle_class=su.SudokuPuzzle)
        newpt.set_test_results(results)
        self.assertEqual(self.pt.get_test_results(), newpt.get_test_results())

    def test_class_repr(self):
        """Class can represent itself"""
        expected = (
            f"PuzzleTester(SudokuPuzzle, test_samples=1, anti_cheat_check=True, "
            f"num_test_cases={len(self.test_cases)}, solver_labels=set())"
        )
        self.assertEqual(expected, repr(self.pt))


if __name__ == "__main__":
    unittest.main()
