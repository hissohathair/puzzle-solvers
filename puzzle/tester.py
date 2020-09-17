"""Implements a PuzzleTester class for tracking the performance of solvers.

The idea is to have a few different algorithms for solving puzzles (e.g.
Sudoku puzzles), and to evaluate their performance against a set of test
cases.

Classes:
    PuzzleTester: Track puzzle solver benchmarking stats.

Functions:
    from_file: Given a file name, read puzzle data and format it into
        the list of dicts expected by PuzzleTester.

    has_same_clues: Given a puzzle and a solution, test that the solution
        is a solution for the actual puzzle, not just some "pre-solved"
        random solution trying to sneak by...
"""

import copy
import timeit

import puzzle.latinsquare as ls


def from_file(filename, level="(not set)"):
    """Load test cases from file, return as list of dicts.

    Puzzle should be formatted as a string on a single line.
    See puzzle.latinsquare.from_string. Trailing whitespace is stripped.

    Args:
        filename: File to read. One line per puzzle.
        level: Label to use for the "difficulty level" when loading this
            data. Optional.

    Returns:
        A list of dictionaries. Dictionary keys are puzzle (containing puzzle
        string); label (filename and line number of puzzle); and
        level (as passed to this function)
    """
    ret = []
    i = 0
    with open(filename) as f:
        for line in f:
            i += 1
            tc = {"puzzle": line.rstrip(), "label": f"{filename}:{i}", "level": level}
            ret.append(tc)
    return ret


def has_same_clues(puzzle, solution):
    """Returns true if the cells in puzzle have the same value in solution.

    Args:
        puzzle: The original puzzle, expected to have some empty cells.
        solution: The solved puzzle.

    Returns:
        True if every non-empty cell in puzzle has the same value in
        solution.
    """
    if puzzle.max_value != solution.max_value:
        return False

    for x in range(puzzle.max_value):
        for y in range(puzzle.max_value):
            if not puzzle.is_empty(x, y) and puzzle.get(x, y) != solution.get(x, y):
                return False
    return True


class PuzzleTester:
    """Creates a PuzzleTester which will track how long a solver takes.

    Attributes:
        puzzle_class: Class passed on init. New instances of this class are
            created for each test run.
        test_samples: Number of times to run each test per solver and test
            case.

    Args:
        puzzle_class: Tester will create new instances of this class for
            the solver. Class should be derived from ConstraintPuzzle.
        test_samples: Number of times to repeat each test case. Default is 1.
    """

    def __init__(self, puzzle_class, test_samples=1):
        self.__last_was_solved = False
        self.puzzle_class = puzzle_class
        self.test_samples = test_samples
        self._test_cases = []
        self._rkeys = ["label", "level", "starting_clues"]
        self._results = {}
        for k in self._rkeys:
            self._results[k] = []

    def num_test_cases(self):
        """Return the number of test cases added so far"""
        return len(self._test_cases)

    def add_test_cases(self, test_cases):
        """Adds a list of test_cases to be used when `run_tests` is called.

        Args:
            test_cases: A list of dictionary objects with the follow keys
                in each dict:
                    - 'label'   Name of test case
                    - 'level'   Difficulty of test case
                    - 'puzzle'  Starting puzzle grid (string format)
                Only 'puzzle' is required to have a valye. The others keys
                will be assigned defaults if missing.

        Returns:
            Total number of test cases now accumulated.

        Raises:
            ValueError: test_cases not a list of dicts.
        """
        if not isinstance(test_cases, list):
            raise ValueError("Expecting a list of dicts (not a list)")
        if not isinstance(test_cases[0], dict):
            raise ValueError("Expecting a list of dicts (is a list, not of dicts")

        # This structure used to keep all test cases
        self._test_cases += test_cases

        # This structure used to track test results for different solvers
        for i, case in enumerate(test_cases):
            if "label" not in case:
                case["label"] = f"Test Case #{i}"
            if "level" not in case:
                case["level"] = "(not set)"
            case["starting_clues"] = ls.count_clues(case["puzzle"])

            for k in self._rkeys:
                self._results[k].append(case[k])

        return len(self._test_cases)

    def run_single_test(self, test_puzzle, solver):
        """Run a single test case.

        Method will create a new instance of a puzzle, using the puzzle_class
        passed on initialization. This method is called by run_tests.

        The method will check that the "solved" puzzle bears at least a
        passing resemblence to the original puzzle, so the solver can't
        "cheat" by just over-writing all cells with a preset pattern.

        Args:
            test_puzzle: String containing test puzzle, will be converted
                using puzzle.latinsquare.from_string.

            solver_instance: Instance of a solver class with a solve() method.

        Returns:
            True if puzzle was solved by solver
        """

        # Initialize puzzle, and make a copy for checking with later
        puz = self.puzzle_class(starting_grid=ls.from_string(test_puzzle))
        orig = copy.deepcopy(puz)

        # Call solver and check for cheating
        claimed_solved = solver.solve(puz)
        if claimed_solved and has_same_clues(orig, puz):
            self.__last_was_solved = puz.is_solved()
        else:
            self.__last_was_solved = False
        return self.__last_was_solved

    def run_tests(self, solver, label=None, callback=None):
        """Run all test cases against the solver.

        Test results are stored internally and can be fetched after
        run_tests returns in a format suitable for passing directly to
        pandas.DataFrame.

        Args:
            solver: Instance of the solver class to test. Must have a method
                solve() -- apart from that no checks are made.

            label: String to use to describe this solver and track results.
                Will default to solver's class name.

            callback: Function to call just prior to running each test case.
                It's also called one more time when all tests done. Callback
                function will be passed the following:
                    label: Same string given to this method, or name of solver
                    num_tests: Number of puzzles test so far
                    total_tests: Total number of puzzles that will be tested
                    total_time: Cummulative time spent so far
                    test_label: Test case label that is about to be tested.
                One final call to callback is done once the tests are
                complete. This can be detected because test_label will be None.

        Returns:
            Number of test cases run.

        Raises:
            ValueError: solver does not have a solve() method.
        """

        solver_method = getattr(solver, "solve", None)
        if not callable(solver_method):
            raise ValueError("solver has no solve() method")

        if not label:
            label = solver.__class__.__name__

        self._results[label] = []

        num_puzzles = 0
        total_time = 0
        for test_case in self._test_cases:
            if callback:
                callback(label, num_puzzles, self.num_test_cases(), total_time, test_case['label'])

            self.__last_was_solved = False
            t = timeit.timeit(
                "pt.run_single_test(test_case['puzzle'], solver)",
                number=self.test_samples,
                globals={
                    "pt": self,
                    "test_case": test_case,
                    "solver": solver,
                },
            )
            num_puzzles += 1
            total_time += t
            if self.__last_was_solved:
                self._results[label].append(t / self.test_samples)
            else:
                self._results[label].append(None)

        # Tests are complete - final call to callback lets cleanup happen
        if callback:
            callback(label, num_puzzles, self.num_test_cases(), total_time, None)
        return num_puzzles

    def get_test_results(self):
        """Return the test results structure. Can be passed directly to pandas.DataFrame"""
        return self._results

    def get_solver_labels(self):
        """Return the solvers that have been tested so far"""
        return set(self._results.keys()) - set(self._rkeys)

    def set_test_results(self, results):
        """Initialise the test results structure.

        Useful for loading previously saved times from a Pandas DataFrame.
        For example:
            pt.set_test_results(df.to_dict('list'))

        Args:
            results: Dictionary if list values for test results.
        """
        self._results = results
