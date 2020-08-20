# puzzlegrid.py
#
# Base class for common 2D constraint-solving puzzle grids
# (e.g. sudoku; kenken)
#

import timeit

DEFAULT_PUZZLE_SIZE = 9
MAX_PUZZLE_SIZE = 25
MIN_PUZZLE_SIZE = 1
EMPTY_CELL = None
MIN_CELL_VALUE = 1
CELL_VALUES = '123456789ABCDEFGHIJKLMNOP'


def build_empty_grid(grid_size):
    """Builds a grid_size X grid_size matrix, with each cell set to EMPTY_CELL"""
    assert not EMPTY_CELL
    assert grid_size >= MIN_PUZZLE_SIZE
    ret = [[] for x in range(grid_size)]
    for x in range(grid_size):
        ret[x] = [EMPTY_CELL for y in range(grid_size)]

    return ret


def char2int(c):
    """Convert character `c` to an int representation:
        - 1-9   Converted to int
        - A-P   Converted to int where A=10, B=11, ... P=25
        - 0|.   Converted to EMPTY_CELL
    """
    if c == '.' or c == '0':
        return EMPTY_CELL
    else:
        return CELL_VALUES.index(c) + 1


def int2char(i):
    """Given an integer from 1..MAX_PUZZLE_SIZE return a corresponding char
        - 1-9   Returned as string
        - 0     Converted to "."
        - 10+   Converted to A..Z (10=A; 11=B; etc.)
    """
    if not i:
        return "."
    else:
        return CELL_VALUES[i-1]


def count_clues(puzzle_grid):
    """Counts clues in a puzzle_grid, which can be a list of lists or string"""
    if isinstance(puzzle_grid, list):
        return sum([1 for sublist in puzzle_grid for i in sublist if i])
    else:
        return len(puzzle_grid) - puzzle_grid.count(".")


def from_file(filename, level="(not set)"):
    """Load test cases from file, return as list of dicts"""
    ret = []
    i = 0
    with open(filename) as f:
        for line in f:
            i += 1
            tc = {'puzzle': line.rstrip(), 'label': f"{filename}:{i}", 'level': level}
            ret.append(tc)
    return ret


class ConstraintPuzzle(object):
    def __init__(self, grid_size=DEFAULT_PUZZLE_SIZE, starting_grid=None):
        """Creates a puzzle grid, `grid_size` X `grid_size` (default 9)"""
        if grid_size < MIN_PUZZLE_SIZE or grid_size > MAX_PUZZLE_SIZE:
            raise ValueError(
                f"grid_size={grid_size} outside allowed ranage [{MIN_PUZZLE_SIZE}:{MAX_PUZZLE_SIZE}]"
            )

        # Basic grid
        self._max_cell_value = grid_size
        self._grid = build_empty_grid(grid_size)
        self._num_empty_cells = grid_size * grid_size

        # Initialize constraints
        self._complete_set = set(range(MIN_CELL_VALUE, grid_size + 1))
        self._allowed_values_for_row = [
            set(self._complete_set) for i in range(grid_size)
        ]
        self._allowed_values_for_col = [
            set(self._complete_set) for i in range(grid_size)
        ]

        # Accept a starting puzzle
        if starting_grid:
            self.init_puzzle(starting_grid)
        return

    def max_value(self):
        """Returns max value for a cell, which is the grid size"""
        return self._max_cell_value

    def init_puzzle(self, starting_grid):
        """Initializes a puzzle grid based on contents of `starting_grid`

        starting_grid:  Can be either a string or 2D array (list of lists of 
                        ints)
        """
        if isinstance(starting_grid, list):
            self.init_puzzle_from_grid(starting_grid)
        else:
            self.init_puzzle_from_str(starting_grid)
        return

    def init_puzzle_from_str(self, starting_grid):
        """Initializes a puzzle grid from a flat string representation

        Example: '89.4...5614.35..9.......8..9.....'.
        """
        self.clear_all()

        s = starting_grid.rstrip()  # convenient to strip trailing whitespace
        if len(s) != self.num_cells():
            raise ValueError(f"starting_grid needs {self.num_cells()}, got {len(s)}")

        for i, ch in enumerate(s):
            v = char2int(ch)
            if v:
                self.set(i // self._max_cell_value, i % self._max_cell_value, v)

        return

    def init_puzzle_from_grid(self, starting_grid):
        """Initializes a puzzle grid to the 2D array passed in `starting_grid`

        Raises ValueError exception if the new starting_grid is the wrong size, 
        or violates a constraint
        """
        self.clear_all()

        # Check that new grid is correct number of rows
        if len(starting_grid) != self._max_cell_value:
            raise ValueError(
                f"starting_grid has {len(starting_grid)} rows, exepect {self._max_cell_value}"
            )

        # Check that new grid has correct number of cols
        for x, row in enumerate(starting_grid):
            if len(row) != self._max_cell_value:
                raise ValueError(
                    f"starting_grid row {x} has {len(row)} values, expect {self._max_cell_value}"
                )

            for y, val in enumerate(row):
                if val:
                    self.set(x, y, val)
        return

    def num_empty_cells(self):
        """Returns the number of empty cells remaining"""
        return self._num_empty_cells

    def num_cells(self):
        """Returns the total number of cells in the grid."""
        return self._max_cell_value * self._max_cell_value

    def get(self, x, y):
        """Returns the cell value at (x, y)
        Returning EMPTY_CELL (None) means no value set.
        """
        return self._grid[x][y]

    def set(self, x, y, v):
        """Sets the call at x,y to value v

        The set operation must obey the rules of the contraints. In this class
            - no value can be repeated in a row
            - no value can be repeated in a column
        If a constraint is violated then a ValueError exception is raised.
        """
        if v < MIN_CELL_VALUE or v > self._max_cell_value:
            raise ValueError(f"Value {v} out of range [{MIN_CELL_VALUE}:{self._max_cell_value}]")
        if self._grid[x][y] == v:
            return

        # Clear value first to update constraints
        if self._grid[x][y]:
            self.clear(x, y)

        # Write value if allowed
        if self.is_allowed_value(x, y, v):
            self._grid[x][y] = v
            self._num_empty_cells -= 1
        else:
            raise ValueError(f"Value {v} not allowed at {x},{y} (constraint violation)")

        # Update constraints
        self._allowed_values_for_row[x].remove(v)
        self._allowed_values_for_col[y].remove(v)
        return

    def clear(self, x, y):
        """Clears the value for a cell at x,y"""

        # Is OK to "clear" an already empty cell (no-op)
        if self._grid[x][y] == EMPTY_CELL:
            return

        # Stash previous value then clear cell
        prev = self._grid[x][y]
        self._grid[x][y] = EMPTY_CELL
        self._num_empty_cells += 1

        # Put previous value back into allowed list
        self._allowed_values_for_row[x].add(prev)
        self._allowed_values_for_col[y].add(prev)
        return

    def clear_all(self):
        """Clears the entire puzzle grid"""
        for x in range(self._max_cell_value):
            for y in range(self._max_cell_value):
                self.clear(x, y)
        return

    def is_empty(self, x, y):
        """Returns True if the cell is empty"""
        return self._grid[x][y] == EMPTY_CELL

    def find_empty_cell(self):
        """Returns the next empty cell as tuple (x, y)

        Search starts at 0,0 and continues along the row. Returns at the first
        empty cell found. Returns empty tuple if no empty cells left.
        """
        for i, row in enumerate(self._grid):
            for j, v in enumerate(row):
                if not v:
                    return (i, j)
        return ()

    def next_empty_cell(self):
        """Generator that returns the next empty cell that exists in the grid

        Search starts at 0,0, just like `find_empty_cell` above. However each
        subsequent call will resume where the previous invocation left off
        (assuming this is being called as a generator function). Returns an
        empty tuple at the end of the list.
        """
        for i, row in enumerate(self._grid):
            for j, v in enumerate(row):
                if not v:
                    yield (i, j)
        return ()

    def next_best_empty_cell(self):
        """Generator method that returns the next "best" empty cell

        Next best cell is the one with the fewest possible values. Returns an
        empty tuple when it reaches the end of the list.
        """
        max_possibilities = 1
        while max_possibilities <= self._max_cell_value:
            for i, row in enumerate(self._grid):
                for j, v in enumerate(row):
                    if not v and len(self.get_allowed_values(i, j)) <= max_possibilities:
                        yield (i, j)
            max_possibilities += 1
        return ()

    def get_all_empty_cells(self):
        """Returns the full list of empty cells (list of tuples)

        Convenience method, mainly used in testing. Use generators
        next_empty_cell or next_best_empty_cell instead.
        """
        return [m for m in self.next_empty_cell()]

    def get_row_values(self, x):
        """Return the list of values from row x as a list

        Does not include the empty cells
        """
        return [i for i in self._grid[x] if i != EMPTY_CELL]

    def get_column_values(self, y):
        """Return the list of values from column y as a list

        Does not include the empty cells
        """
        return [i[y] for i in self._grid if i[y] != EMPTY_CELL]

    def get_allowed_values(self, x, y):
        """Returns the current set of allowed values at x,y as a set

        This is based on the intersection of the sets of allowed values for
        the same row and column. If there is already a value in a cell, then
        it is the only allowed value.
        """
        if self._grid[x][y]:
            return {self._grid[x][y]}
        else:
            return self._allowed_values_for_row[x] & self._allowed_values_for_col[y]

    def is_allowed_value(self, x, y, v):
        """Returns True if placing value v at position x,y is allowed

        Allowed values are based on current constraint state. The value might
        still be incorrect, function is only asserting that it is allowed
        based on the current state of the puzzle grid.
        """
        if v and self._grid[x][y] == v:
            return True
        else:
            return v in self.get_allowed_values(x, y)

    def is_puzzle_valid(self):
        """Returns True if the puzzle is in a valid state, False if rules broken

        This fuction should *always* return True, because it should not be
        possible to get into an invalid state. However since caller clould
        always access self._grid directly, and since we could introduce a bug,
        this function can perform an additional check.

        Empty cells are allowed -- this is not checking that the puzzle is
        solved.
        """
        for x in range(self._max_cell_value):
            values = self.get_row_values(x)
            if len(values) != len(set(values)):
                return False

        for y in range(self._max_cell_value):
            values = self.get_column_values(y)
            if len(values) != len(set(values)):
                return False

        return True

    def is_solved(self):
        """Returns True if there are no empty cells left, and the puzzle is valid"""
        return self.is_puzzle_valid() and self.num_empty_cells() == 0

    def as_grid(self):
        """Return a string representation of the puzzle as a 2D grid"""
        blurb = [["-" if v is None else v for v in row] for row in self._grid]
        return "\n".join(" ".join(map(str, sl)) for sl in blurb)

    def __str__(self):
        """Return a flat string representation of the puzzle"""
        return "".join([int2char(i) if i else "." for sublist in self._grid for i in sublist])


class ConstraintSolver(object):
    def __init__(self):
        """Initialize internal state, which is some basic stats counters

        Attributes:
            stats:      Dictionary for internal solver stats
            trace:      Record of moves recorded by solver
        """
        self.stats = {}
        self.trace = []
        return

    def solve(self, puzzle):
        """Solve the `puzzle` (assumed to be a `ConstraintPuzzle`)

        Virtual method to call to solve `puzzle`. Return True if solved, False
        if not able to solve.
        """
        raise NotImplementedError("solve() should be implemented by child class")


class PuzzleTester(object):
    """Track puzzle benchmarking stats"""

    def __init__(self, puzzle_class=ConstraintPuzzle, test_samples=1):
        """Creates a PuzzleTester which will track how long a solver takes.

        Parameters:
            puzzle_class:   Tester will create new instances of this class for
                            the solver. Class should be derived from 
                            ConstraintPuzzle
            test_samples:   Number of times to repeat each test case
        """
        self._puzzle_class = puzzle_class
        self._test_samples = test_samples
        self._test_cases = []
        self._rkeys = ["label", "level", "starting_clues"]
        self._results = {}
        for k in self._rkeys:
            self._results[k] = []
        return

    def num_testcases(self):
        """Return the number of test cases added so far"""
        return len(self._test_cases)

    def add_testcases(self, test_cases):
        """Adds a list of test_cases to be used when `run_tests` is called.

        Parameter `test_cases` is expected to be a list of dictionary
        objects with the follow keys in each dict:
            - 'label'   Name of test case
            - 'level'   Difficulty of test case
            - 'puzzle'  Starting puzzle grid (either a string or 2D array)
        Only 'puzzle' is required, the others will be auto-generated if missing
        """
        if not isinstance(test_cases, list):
            raise ValueError("Expecting a list of dicts (not a list)")
        elif not isinstance(test_cases[0], dict):
            raise ValueError("Expecting a list of dicts (is a list, not of dicts")

        # This structure used to keep all test cases
        self._test_cases += test_cases

        # This structure used to track test results for different solvers
        for i, case in enumerate(test_cases):
            if "label" not in case:
                case["label"] = f"Test Case #{i}"
            if "level" not in case:
                case["level"] = f"(not set)"
            case["starting_clues"] = count_clues(case["puzzle"])

            for k in self._rkeys:
                self._results[k].append(case[k])
        return

    def drop_testcases(self):
        """Drop test cases but keep results"""
        self._test_cases = []
        return

    def run_single_test(self, test_case, puzzle, solver):
        """Run a single test case. Execution of this method is what run_tests is timing

        Method will create a new instance of a puzzle, using the `puzzle_class`
        passed on initialization of the calling instance.

        Returns True if puzzle was solved by solver.solve(p)

        Parameters:
            test_case:  Dict containing test case, must contain 'puzzle'
            solver:     Instance of a ConstraintSolver class with solve() method
        """
        # p = self._puzzle_class(starting_grid=test_case['puzzle'])
        puzzle.init_puzzle(test_case['puzzle'])
        solver.solve(puzzle)
        self._last_was_solved = puzzle.is_solved()
        return self._last_was_solved

    def run_tests(self, solver, label, callback=None):
        """Run all test cases against the `solver` (class ConstraintSolver)

        Returns the number of tests run

        Parameters:
            solver:     Instance of a ConstraintSolver to test
            label:      String to use to describe this solver and track results
            callback:   Function to call just prior to running each test case.
                        It's also called one more time when all tests done.

        Callback function will be passed the following:
            label:          Same string given to this method
            num_puzzles:    Number of puzzles test so far
            num_testcases:  Total number of puzzles that will be tested
            total_time:     Cummulative time spent so far
            test_case:      Test_case (a dict) that is about to be tested
        """
        if not isinstance(solver, ConstraintSolver):
            raise ValueError("Expected a ConstraintSolver")

        self._results[label] = []

        num_puzzles = 0
        total_time = 0
        for test_case in self._test_cases:
            if callback:
                callback(label, num_puzzles, self.num_testcases(), total_time, test_case)

            puzzle = self._puzzle_class()
            self._last_was_solved = False
            t = timeit.timeit(
                "pt.run_single_test(test_case, puzzle, solver)",
                number=self._test_samples,
                globals={
                    "pt": self,
                    "test_case": test_case,
                    "solver": solver,
                    "puzzle": puzzle,
                }
            )
            num_puzzles += 1
            total_time += t
            if self._last_was_solved:
                self._results[label].append(t / self._test_samples)
            else:
                self._results[label].append(None)

        if callback:
            callback(label, num_puzzles, self.num_testcases(), total_time, None)
        return num_puzzles

    def get_test_results(self):
        """Return the test results structure"""
        return self._results
