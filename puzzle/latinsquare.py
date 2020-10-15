"""Implements a class for Latin Square puzzles.

A Latin Square is a square grid of numbers from 1..N, where a number may not
be repeated in the same row or column. Such squares form the basis of puzzles
like Sudoku, Kenken(tm), and their variants.

Classes:
    LatinSquare: Implements a square puzzle constrained by not repeating
        values in the same row or column.

Functions:
    build_empty_grid: Build a 2D array (list of lists) for puzzle.
    char2int: Convert bewteen character and integer representation of a cell value.
    int2char: Reverse of char2int.
    count_clues: Given a string or 2D array representing a puzzle, return
        the number of starting clues in the puzzle.
    from_string: Given a string representing a puzzle, return the 2D array
        equivalent. All class methods expect the array version.
"""

DEFAULT_PUZZLE_SIZE = 9
EMPTY_CELL = None

# Have only tested up to 25x25 so set that max size here
# higher values may work but aren't tested

MAX_PUZZLE_SIZE = 25
MIN_PUZZLE_SIZE = 1
MIN_CELL_VALUE = 1  # 0 evals to False so can be confused with EMPTY_CELL
CELL_VALUES = "123456789ABCDEFGHIJKLMNOP"

assert MAX_PUZZLE_SIZE == len(CELL_VALUES)


def build_empty_grid(grid_size):
    """Builds a 2D array grid_size * grid_size, each cell element is None."""
    assert MIN_PUZZLE_SIZE <= grid_size <= MAX_PUZZLE_SIZE
    ret = [[] for x in range(grid_size)]
    for x in range(grid_size):
        ret[x] = [EMPTY_CELL for y in range(grid_size)]
    return ret


def char2int(char):
    """Converts character char to an int representation."""
    if char in (".", "0"):
        return EMPTY_CELL
    return CELL_VALUES.index(char) + 1


def int2char(value):
    """Converts back from an int value to character value for a cell."""
    if not value:
        return "."
    return CELL_VALUES[value - 1]


def count_clues(puzzle_grid):
    """Counts clues in a puzzle_grid, which can be a list of lists or string."""
    if isinstance(puzzle_grid, list):
        return sum([1 for sublist in puzzle_grid for i in sublist if i])
    return len(puzzle_grid) - puzzle_grid.count(".")


def from_string(puzzle_string):
    """Takes a string and converts it to a list of lists of integers.

    Puzzles are expected to be 2D arrays of ints, but it's convenient to store
    test data as strings (e.g. '89.4...5614.35..9.......8..9.....'). So this
    will split a string (using period for "empty cell") and return the 2D array.

    Args:
        puzzle_string: A string with 1 character per cell. Use uppercase letters
            for integer values >= 10 (A=10; B=11; etc). Trailing blanks are
            stripped.

    Returns:
        A list of lists of ints.

    Raises:
        ValueError: puzzle_string length is not a square (e.g. 4, 9, 16, 25);
            or a character value in string is out of range.
    """
    s = puzzle_string.rstrip()
    grid_size = int(len(s) ** (1 / 2))

    if not MIN_PUZZLE_SIZE <= grid_size <= MAX_PUZZLE_SIZE:
        raise ValueError(f"puzzle_string {grid_size}x{grid_size} is out of range")

    if grid_size ** 2 != len(s):
        raise ValueError(f"puzzle_string {grid_size}x{grid_size} is not a square")

    ret = build_empty_grid(grid_size)
    for i, ch in enumerate(s):
        v = char2int(ch)
        if v and MIN_CELL_VALUE <= v <= grid_size:
            ret[i // grid_size][i % grid_size] = v
        elif v:
            raise ValueError(f"Cell value {v} at {i} out of range [1:{grid_size}]")

    return ret


class LatinSquare:
    """Implements a Latin Square "puzzle".

    A Latin Square is a 2D matrix where the values in each cell cannot be
    repeated in the same row or column.

    Dimensions are always square (ie. width==height==grid_size). If no
    values are passed to constructor, will build an empty grid of size
    DEFAULT_PUZZLE_SIZE (9).

    Attributes:
        size: Dimensions of the square (length, height) in a tuple.
        num_cells: Total number of cells (grid_size * grid_size)
        max_value: Equal to grid_size, it's the max value of a cell, and
            also the grid's length and height.
        complete_set: Set of values from [1..max_value] that must exist once
            in each row and column in a solved puzzle.

    Args:
        starting_grid: A list of lists of integers (2D array of ints).
            Pass None to start with an empty grid.
        grid_size: The number of cells for the width and height of the
            grid. Default value is 9, for a 9x9 grid (81 cells). If not
            set, size is set to len(starting_grid), otherwise must be
            consistent with len(starting_grid) as a check for "bad" data.

    Raises:
        ValueError: An inconsistency exists in the starting_grid;
            or the grid_size is too small or too large (1 to 25)
    """

    def __init__(self, grid_size=None, starting_grid=None):

        # If a starting_grid is passed, that sets the size
        if starting_grid and grid_size:
            if len(starting_grid) != grid_size:
                raise ValueError(f"starting_grid is not {grid_size}x{grid_size}")
        elif starting_grid:
            grid_size = len(starting_grid)
        elif grid_size is None:
            grid_size = DEFAULT_PUZZLE_SIZE

        if not MIN_PUZZLE_SIZE <= grid_size <= MAX_PUZZLE_SIZE:
            raise ValueError(
                f"grid_size={grid_size} outside [{MIN_PUZZLE_SIZE}:{MAX_PUZZLE_SIZE}]"
            )

        # Attributes
        self.size = (grid_size, grid_size)
        self.num_cells = grid_size * grid_size
        self.max_value = grid_size
        self.complete_set = set(range(MIN_CELL_VALUE, grid_size + 1))

        # Protected
        self._grid = build_empty_grid(grid_size)
        self.__num_empty_cells = grid_size * grid_size

        # Initialize constraints
        self.__allowed_values_for_row = [
            set(self.complete_set) for i in range(grid_size)
        ]
        self.__allowed_values_for_col = [
            set(self.complete_set) for i in range(grid_size)
        ]

        # Accept a starting puzzle
        if starting_grid:
            self.init_puzzle(starting_grid)

    def init_puzzle(self, starting_grid):
        """Initializes a puzzle grid based on contents of starting_grid.

        Clears the existing puzzle and resets internal state (e.g. count of
        empty cells remaining).

        Args:
            starting_grid: A list of lists of integers (2D array of ints).
                To help catch data errors, must be the same size as what the
                instance was initialized for.

        Raises:
            ValueError: Size of starting_grid (len) is not what was expected
                from the initial grid_size; or constraint on cell values is
                violated (e.g. dupicate value in a row)
        """
        self.clear_all()

        # Check that new grid is correct number of rows
        if len(starting_grid) != self.max_value:
            raise ValueError(f"Exepect {self.max_value} rows, got {len(starting_grid)}")

        # Check that new grid has correct number of cols
        for x, row in enumerate(starting_grid):
            if len(row) != self.max_value:
                raise ValueError(
                    f"Expect {self.max_value} columns in row {x}, got {len(row)}")

            for y, val in enumerate(row):
                if val:
                    self.set(x, y, val)

    def num_empty_cells(self):
        """Returns the number of empty cells remaining."""
        return self.__num_empty_cells

    def get(self, x, y):
        """Returns the cell value at (x, y)"""
        return self._grid[x][y]

    def set(self, x, y, value):
        """Sets the call at x,y to value

        The set operation must obey the rules of the contraints. In this class
            - no value can be repeated in a row
            - no value can be repeated in a column
        If a constraint is violated then a ValueError exception is raised.

        Args:
            x, y: Cell position in row, column order.
            value: Integer value to write into the cell.

        Raises:
            ValueError: Cell value out of range [1:max_value]
            IndexError: x,y location out of range [0:max_value-1]
        """
        if value < MIN_CELL_VALUE or value > self.max_value:
            raise ValueError(f"Value {value} out of range [{MIN_CELL_VALUE}:{self.max_value}]")

        if self._grid[x][y] == value:
            return

        # Clear value first to update constraints
        if self._grid[x][y]:
            self.clear(x, y)

        # Write value if allowed
        if value in self.get_allowed_values(x, y):
            self._grid[x][y] = value
            self.__num_empty_cells -= 1
        else:
            raise ValueError(f"Value {value} not allowed at {x},{y}")

        # Update constraints
        self.__allowed_values_for_row[x].remove(value)
        self.__allowed_values_for_col[y].remove(value)

    def clear(self, x, y):
        """Clears the value for a cell at x,y and update constraints"""

        # Is OK to "clear" an already empty cell (no-op)
        if self._grid[x][y] == EMPTY_CELL:
            return

        # Stash previous value before clearing, to update constraints
        prev = self._grid[x][y]
        self._grid[x][y] = EMPTY_CELL
        self.__num_empty_cells += 1

        # Put previous value back into allowed list
        self.__allowed_values_for_row[x].add(prev)
        self.__allowed_values_for_col[y].add(prev)

    def clear_all(self):
        """Clears the entire puzzle grid"""
        for x in range(self.max_value):
            for y in range(self.max_value):
                self.clear(x, y)

    def is_empty(self, x, y):
        """Returns True if the cell is empty"""
        return self._grid[x][y] == EMPTY_CELL

    def find_empty_cell(self):
        """Returns the next empty cell as tuple (x, y)

        Search starts at 0,0 and continues along the row. Returns at the first
        empty cell found. Returns empty tuple if no empty cells left.
        """
        for x, row in enumerate(self._grid):
            for y, v in enumerate(row):
                if not v:
                    return (x, y)
        return ()

    def next_empty_cell(self):
        """Generator that returns the next empty cell that exists in the grid

        Search starts at 0,0, just like `find_empty_cell`. However each
        subsequent call will resume where the previous invocation left off
        (assuming this is being called as a generator function). Returns an
        empty tuple at the end of the list.
        """
        for x, row in enumerate(self._grid):
            for y, v in enumerate(row):
                if not v:
                    yield (x, y)
        return ()

    def next_best_empty_cell(self):
        """Generator method that returns the next "best" empty cell

        Next best cell is the one with the fewest possible values. Returns an
        empty tuple when it reaches the end of the list.
        """
        max_possibilities = 1
        while max_possibilities <= self.max_value:
            for x, row in enumerate(self._grid):
                for y, v in enumerate(row):
                    if not v and len(self.get_allowed_values(x, y)) <= max_possibilities:
                        yield (x, y)

            max_possibilities += 1
        return ()

    def get_row_values(self, x):
        """Return the list of set values from row x as a list"""
        return [i for i in self._grid[x] if i != EMPTY_CELL]

    def get_column_values(self, y):
        """Return the list of set values from column y as a list"""
        return [i[y] for i in self._grid if i[y] != EMPTY_CELL]

    def get_allowed_values(self, x, y):
        """Returns the current set of allowed values at x,y as a set

        This is based on the intersection of the sets of allowed values for
        the same row and column. If there is already a value in a cell, then
        it is the only allowed value.
        """
        if self._grid[x][y]:
            return {self._grid[x][y]}
        return self.__allowed_values_for_row[x] & self.__allowed_values_for_col[y]

    def is_valid(self):
        """Returns True if the puzzle is in a valid state, False if rules broken.

        This fuction should *always* return True, because it should not be
        possible to get into an invalid state. However since caller clould
        always access self._grid directly, and since we could introduce a bug,
        this function can perform an additional check.

        Empty cells are allowed -- this is not checking that the puzzle is
        solved.
        """
        for x in range(self.max_value):
            values = self.get_row_values(x)
            if len(values) != len(set(values)):
                return False

        for y in range(self.max_value):
            values = self.get_column_values(y)
            if len(values) != len(set(values)):
                return False

        return True

    def is_solved(self):
        """Returns True if there are no empty cells left, and the puzzle is valid"""
        if self.is_valid():
            for i in range(self.max_value):
                for j in range(self.max_value):
                    if self.is_empty(i, j):
                        return False
            return True
        return False

    def __str__(self):
        """Return a string representation of the puzzle as a 2D grid"""
        blurb = [["-" if v is None else v for v in row] for row in self._grid]
        return "\n".join(" ".join(map(str, sl)) for sl in blurb)

    def __repr__(self):
        """Return an unambiguous string representation of the puzzle"""
        puz = "".join([int2char(i) for sublist in self._grid for i in sublist])
        ret = f"{self.__class__.__name__}({self.max_value}, '{puz}')"
        return ret
