"""Implements classes for Sudoku puzzles and solvers.

A SudokuPuzzle is a LatinSquare with additional constraints for "boxes"
which are 3x3 groups of cells (in a standard 9x9 Sudoku).

Module Constants:
    SOLVERS: Dictionary of solving algorithms and their associated classes.
    SAMPLE_PUZZLES: List of dictionaries containing SudokuPuzzles.

Classes:
    SudokuPuzzle: Implements a Sudoku puzzle and enforces the constraints
        when setting cells. Default puzzle size is 9x9 but has been tested
        from 4x4 to 25x25.

    SudokuSolver: Helper class that takes a method as a parameter and
        initializes one of the solver classes below.

    BacktrackingSolver: Given a SudokuPuzzle, will solve the puzzle using
        a backtracking algorithm. Caution: can be very slow on larger puzzles.

    ConstraintPropogationSolver: Solves a SudokuPuzzle using backtracking,
        but also takes advantage of knowing the constraints that exist
        on cell values. The SudokuPuzzle itself propogates constraints as
        cell values are filled in.

    DeductiveSolver: Uses deductive techniques to try and solve a SudokuPuzzle
        before falling back to ConstraintPropogation to fill in the remaining
        cells.

    SATSolver: Converts a SudokuPuzzle to a set of SAT clauses and then passes
        those to pycosat for solving. Fastest and most consistent performer.
"""

import collections
import pycosat

from puzzle.latinsquare import LatinSquare, from_string, build_empty_grid


DEFAULT_SUDOKU_SIZE = 9


class SudokuPuzzle(LatinSquare):
    """Implements a Sudoku puzzle grid as a specialized LatinSquare.

    The class will enforce the rules of standard Sudoku, meaning no
    value can be repeated in a row, column, or box. If both grid_size and
    starting_grid are set then they must be consistent (i.e. grid_size
    must == len(starting_grid)), this is done as a data integrity check.
    Otherwise the caller can define one param and the other will be set
    to match.

    Attributes:
        box_size: Length of a "box" in the puzzle. Always the square root
            of the grid_size.
        size: Dimensions of the puzzle (inherited).
        num_cells: Total number of cells (grid_size * grid_size).
        max_value: Highest value allowed in a cell, therefore also used
            as the puzzle's width and height.
        complete_set: Set of values from [1..max_value] that must exist once
            in each row, column, and box in a solved puzzle.

    Args:
        grid_size: The width/height of the grid (default is 9). Must be a
            square value (i.e. 1, 4, 9, 16, or 25) for Sudoku.
        starting_grid: A list of lists of integers (2D array of ints) that
            represents the starting clues.

    Raises:
        ValueError: There is an inconsistency in the grid_size and/or
            starting_grid; or the starting clues violate a constraint.
    """

    def __init__(self, grid_size=None, starting_grid=None):

        # Convert starting_grid
        if isinstance(starting_grid, str):
            starting_grid = from_string(starting_grid)

        # If both parameters are passed, they need to be consistent
        if grid_size and starting_grid:
            if len(starting_grid) != grid_size:
                raise ValueError(f"starting_grid is not {grid_size}x{grid_size}")
        elif starting_grid:
            grid_size = len(starting_grid)
        elif grid_size is None:
            grid_size = DEFAULT_SUDOKU_SIZE

        # Box is square root, check that grid_size is also a square number
        self.box_size = int(grid_size ** (1 / 2))
        if self.box_size ** 2 != grid_size:
            raise ValueError(f"grid_size={grid_size} is not a square number")

        # Start by initialising LatinSquare super, use it to calculate
        # the box size. starting_grid has to be blank, because we're not ready
        # to set the box constraints yet.

        blank_grid = build_empty_grid(grid_size)
        super().__init__(grid_size=grid_size, starting_grid=blank_grid)

        # Super has initialised row and column constraints. Sudoku puzzles
        # have an extra constraint -- boxes cannot contain repeated values.

        self.__allowed_values_for_box = [
            set(self.complete_set) for i in range(grid_size)
        ]

        # Now it's safe to copy in the starting_grid, which will update the
        # constraints on rows, columns, boxes

        if starting_grid:
            self.init_puzzle(starting_grid)

    def box_num_to_xy(self, i):
        """Given a box number, return the row and column for its top left position.

        Boxes are numbered from 0 to max_value-1, starting with 0 in the top left,
        then running left to right and down the rows. For example in a 9x9
        puzzle:
            0 (0,0)   1 (0, 3)   2 (0, 6)
            3 (3,0)   4 (3, 3)   5 (3, 6)
            6 (6,0)   7 (6, 3)   8 (6, 6)

        Returns:
            Row and column of box starting position, as tuple.
        """
        x = (i // self.box_size) * self.box_size
        y = (i % self.box_size) * self.box_size
        return (x, y)

    def box_xy_to_num(self, x, y):
        """Given a cell at x,y return what the sequential box number is.

        See box_num_to_xy for how boxes are laid out.

        Returns:
            An integer from [0:max_value-1]
        """
        box_x = x // self.box_size
        box_y = y // self.box_size
        return (box_x * self.box_size) + box_y

    def set(self, x, y, value):
        """Sets value of cell (x,y) to value, updating constraints.

        Calls the parent (LatinSquare) set method first, then updates the
        box's constraints.
        """
        if self._grid[x][y] == value:
            return
        super().set(x, y, value)

        # Update box constraints
        self.__allowed_values_for_box[self.box_xy_to_num(x, y)].remove(value)

    def clear(self, x, y):
        """Clears the value at x,y. Will update the box constraints."""
        if not self._grid[x][y]:
            return

        # Stash previous value, then clear cell
        prev = self._grid[x][y]
        super().clear(x, y)

        # This value available again for this box
        self.__allowed_values_for_box[self.box_xy_to_num(x, y)].add(prev)

    def get_box_values(self, box_num):
        """Return the list of set (non-empty) values from the box box_num."""
        box_x, box_y = self.box_num_to_xy(box_num)

        # Extracts 2D array
        values = [
            i[box_y:box_y + self.box_size]
            for i in self._grid[box_x:box_x + self.box_size]
        ]

        # Flattens list
        return [i for sublist in values for i in sublist if i]

    def get_allowed_values(self, x, y):
        """Returns the current set of possible values at x, y.

        Set of current allowed values is based on the intersection of the sets
        of allowed values for the same row, column and box. If there is a value
        set in this cell, then it is the only allowed value, regardless of
        the values of neighbouring cells.

        Returns:
            A set of values. Values will be within [1:max_value].
        """
        if self._grid[x][y]:
            return set([self._grid[x][y]])
        else:
            return (
                super().get_allowed_values(x, y)
                & self.__allowed_values_for_box[self.box_xy_to_num(x, y)]
            )

    def is_valid(self):
        """Returns True if the puzzle is still valid (i.e. obeys the rules).

        Empty cells are allowed, compare is_solved. This method should *always*
        return True, since it should not be possible to put a puzzle into an
        invalid state (not without accessing self._grid directly...)

        Returns:
            True, unless programmer error.
        """

        # We only need to check the box constraint (parent class does rows
        # and columns already).

        for box in range(self.max_value):
            values = self.get_box_values(box)
            if len(values) != len(set(values)):
                return False

        return super().is_valid()

    def as_html(self, show_possibilities=0):
        """Renders the current puzzle in simple HTML table.

        Sets the table class to "sudoku", and if the puzzle is solved sets
        the additional class "solved".

        Args:
            show_possibilities: If > 0, then cells with possible values
                less than or equal to that will show the possible values.

        Returns:
            String containing a HTML table.
        """
        data = []
        for x in range(self.max_value):
            row_to_show = []
            for y in range(self.max_value):
                if not self.is_empty(x, y):
                    row_to_show.append(self.get(x, y))
                elif len(self.get_allowed_values(x, y)) <= show_possibilities:
                    row_to_show.append(self.get_allowed_values(x, y))
                else:
                    row_to_show.append(" ")
            data.append(row_to_show)

        css_class = "sudoku"
        if self.is_solved():
            css_class += " solved"

        ret = '<table class="{}"><tr>{}</tr></table>'.format(
            css_class,
            "</tr><tr>".join(
                "<td>{}</td>".format("</td><td>".join(str(_) for _ in row))
                for row in data
            ),
        )
        return ret


# SOLVERS dict is filled in by @register_solver decorator

SOLVERS = dict()


def register_solver(cls):
    """Register class as a solver, populating SOLVERS. Private function."""
    idx = cls.__name__.replace("Solver", "").lower()
    SOLVERS[idx] = cls
    return cls


@register_solver
class BacktrackingSolver:
    """Solve a Sudoku puzzle using backtracking.

    Attributes:
        max_depth: Maximum level of recursion reached during backtracking.
        backtrack_count: Number of times solve had to "backtrack" because
            an initial guess proved to be wrong.
    """

    def __init__(self):
        self.max_depth = 0
        self.backtrack_count = 0

    def solve(self, puzzle):
        """Solve the puzzle using backtracking.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            Should always return True (backtracking always works...eventually).
        """
        if puzzle.is_solved():
            return True
        self.max_depth = 0
        self.backtrack_count = 0
        return self._solve_backtracking(puzzle)

    def _solve_backtracking(self, puzzle, depth=0):
        """Internal method that implements the actual backtracking algorithm.

        Returns:
            True if no empty cells left, and no constraint violations made
            in the current recursive "search path".
        """

        if puzzle.num_empty_cells() == 0:
            return True

        if depth > self.max_depth:
            self.max_depth = depth

        x, y = puzzle.find_empty_cell()
        for value in puzzle.get_allowed_values(x, y):
            puzzle.set(x, y, value)
            if self._solve_backtracking(puzzle, depth=depth + 1):
                return True
            else:
                puzzle.clear(x, y)
                self.backtrack_count += 1

        return False


@register_solver
class ConstraintPropogationSolver(BacktrackingSolver):
    """Solve a Sudoku puzzle using constraint propogation and backtracking.

    Overrides the parent class's simple backtracking with a method that
    considers the constraints being updated in the puzzle class.

    Attributes (inherited from BacktrackingSolver):
        max_depth: Maximum level of recursion reached during backtracking.
        backtrack_count: Number of times solve had to "backtrack" because
            an initial guess proved to be wrong.
    """

    def _solve_backtracking(self, puzzle, depth=0):
        """Internal method that implements the actual backtracking algorithm.

        Returns:
            True if no empty cells left, and no constraint violations made
            in the current recursive "search path".
        """

        if puzzle.num_empty_cells() <= 0:
            return True

        if depth > self.max_depth:
            self.max_depth = depth

        # Generator function will return cells with only 1 possible value
        # first, then 2, and so on...

        mtGen = puzzle.next_best_empty_cell()
        try:
            x, y = next(mtGen)
        except StopIteration:
            return True  # TODO: Not sure this is needed, we never reach here

        for value in puzzle.get_allowed_values(x, y):
            puzzle.set(x, y, value)
            if self._solve_backtracking(puzzle, depth=depth + 1):
                return True
            else:
                puzzle.clear(x, y)
                self.backtrack_count += 1

        return False


@register_solver
class DeductiveSolver(ConstraintPropogationSolver):
    """Attempt to solve the puzzle using deductive techniques.

    There are three techniques implemented here so far:

        solve_single_possibilities: Looks for cells with only 1 possible value
            remaining and fills those in. Repeats until no more cells can be
            solved this way.

        solve_only_squares: Looks for values that can only go into one possible
            cell in a given row, column, or box. Called "only squares" in the
            Sudoku strategy guide.

        solve_two_out_of_three: Looks at groups of 3 rows or columns for values
            that occur twice, then deduces where the third value must go based
            on allowed values remaining.

    Attributes:
        use_backtracking: Whether backtracking fallback has been enabled.

    Args:
        use_backtracking: If True, solve method will fall back to
            constraint propogation if the deductive methods do not
            completely solve the puzzle.
    """

    def __init__(self, use_backtracking=True):
        self.use_backtracking = use_backtracking

    def solve(self, puzzle):
        """Solve the puzzle. Return True if solved, False otherwise.

        Different deductive techniques are called. When they stop yielding
        results, we'll call the parent class solve() to use constraint
        propogation.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            If puzzle was solved. Unlike other solution methods this will
            sometimes be False.
        """
        if puzzle.is_solved():
            return True

        # Exhaust the deductive techniques first
        num_cells_updated = 1
        while num_cells_updated > 0:
            num_cells_updated = 0
            num_cells_updated += self.solve_single_possibilities(puzzle)
            num_cells_updated += self.solve_only_squares(puzzle)
            num_cells_updated += self.solve_two_out_of_three(puzzle)

        # Deductive methods can't do any more - go to fall back if needed
        if puzzle.is_solved():
            return True
        elif self.use_backtracking:
            return super().solve(puzzle)
        else:
            return puzzle.is_solved()

    def solve_single_possibilities(self, puzzle):
        """Set cell values for cells which have one possible value.

        Single possibilities are those cells for which there is only one
        possible value, all others already exist in that row, column or box.
        This is sometimes enough to solve very easy Sudoku puzzles.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            The number of cells that were set on this call.
        """
        # Keep trying until we are no longer able to solve cells
        num_cells_updated = 1
        total_cells_updated = 0
        while num_cells_updated > 0:
            num_cells_updated = 0
            for m in puzzle.next_best_empty_cell():
                possibles = puzzle.get_allowed_values(*m)
                if len(possibles) == 1:
                    (value,) = possibles
                    puzzle.set(*m, value)
                    num_cells_updated += 1
            total_cells_updated += num_cells_updated

        return total_cells_updated

    def solve_only_squares(self, puzzle):
        """Look for values that can only go in one possible cell in a region.

        Examines each row, column, and box, looking for values that can only
        go in one possible cell in that region. This method can solve easy to
        intermediate puzzles on its own, but will struggle with hard or
        difficult puzzles.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            The number of cells that were set on this call.
        """

        # A region is a row, column, or box. Calls the group-specific methods
        # below. Keeps trying until the method fails to solve any new cells

        num_cells_updated = 1
        total_cells_updated = 0
        while num_cells_updated > 0:
            num_cells_updated = (
                self._solve_only_row_squares(puzzle)
                + self._solve_only_column_squares(puzzle)
                + self._solve_only_box_squares(puzzle)
            )
            total_cells_updated += num_cells_updated

        return total_cells_updated

    # TODO: The algorithm in the next three methods is essentially the same.
    # There must be a DRYer way in Python...

    def _solve_only_row_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the row

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for x in range(puzzle.max_value):
            # What hasn't this row got?
            missing = puzzle.complete_set - set(puzzle.get_row_values(x))

            # How many places on this row could each missing value go?
            for value in missing:
                possible_cells = []
                for y in range(puzzle.max_value):
                    if puzzle.is_empty(x, y) and value in puzzle.get_allowed_values(x, y):
                        possible_cells.append((x, y))

                # only one possible location?
                if len(possible_cells) == 1:
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], value)

        return num_cells_updated

    def _solve_only_column_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the column

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for y in range(puzzle.max_value):
            # What hasn't this column got?
            missing = puzzle.complete_set - set(puzzle.get_column_values(y))

            # How many places in this column could each missing value go?
            for value in missing:
                possible_cells = []
                for x in range(puzzle.max_value):
                    if puzzle.is_empty(x, y) and value in puzzle.get_allowed_values(x, y):
                        possible_cells.append((x, y))

                # Only one possible location?
                if len(possible_cells) == 1:
                    # print(f"Column {y} needs a {v} and it can only go here {possible_cells}", file=sys.stderr)
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], value)

        return num_cells_updated

    def _solve_only_box_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the box

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for box in range(puzzle.max_value):
            # What hasn't this box got?
            missing = puzzle.complete_set - set(puzzle.get_box_values(box))

            # How many places in this box could each missing value go?
            for value in missing:
                possible_cells = []
                box_x, box_y = puzzle.box_num_to_xy(box)
                for x in range(box_x, box_x + puzzle.box_size):
                    for y in range(box_y, box_y + puzzle.box_size):
                        if puzzle.is_empty(x, y) and value in puzzle.get_allowed_values(x, y):
                            possible_cells.append((x, y))

                # Only one possible location?
                if len(possible_cells) == 1:
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], value)

        return num_cells_updated

    def solve_two_out_of_three(self, puzzle):
        """Look at rows and columns in groups of 3, to determine possible cells.

        Examines rows and columns in groups of 3 adjacent regions. For those
        values that exist in 2/3 regions, see if there is only one remaining
        location for that value in the 3rd region.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            The number of cells that were set on this call.
        """
        num_cells_updated = 1
        total_cells_updated = 0
        while num_cells_updated > 0:
            num_cells_updated = (
                self._solve_two_out_of_three_by_rows(puzzle) 
                + self._solve_two_out_of_three_by_columns(puzzle)
            )
            total_cells_updated += num_cells_updated

        return total_cells_updated

    # TODO: Again, this algorithm is the same for rows/cols, so must be a
    # better way to do this in Python than repeating ourselves...

    def _solve_two_out_of_three_by_rows(self, puzzle):
        """Take 3 rows at a time, and find digits that are solved in 2 of them."""

        num_cells_updated = 0

        # Take 3 rows at a time (the box size)
        for x in range(0, puzzle.max_value, puzzle.box_size):
            solved_cells = []
            for i in range(puzzle.box_size):
                solved_cells += puzzle.get_row_values(x + i)

            # Which values appear twice, and therefore missing in 1 row only?
            counter = collections.Counter(solved_cells)
            for val in [x for x in counter.keys() if counter[x] == puzzle.box_size - 1]:
                # Which row is missing the val? Which box?
                rows = set(range(x, x + puzzle.box_size))
                boxes = set(range(puzzle.box_size))
                for i in range(puzzle.box_size):
                    row_values = puzzle.get_row_values(x + i)
                    if val in row_values:
                        rows.remove(x + i)
                        for y in range(puzzle.max_value):
                            if puzzle.get(x + i, y) == val:
                                boxes.remove(y // puzzle.box_size)

                # Lordy. OK, at least now we have 1 row and 3 cells which *could*
                # take the value val. See if there is only 1 cell to put it in

                assert len(rows) == 1
                assert len(boxes) == 1
                (row,) = rows
                (box,) = boxes

                cells = []
                for y in range(box * puzzle.box_size, (box * puzzle.box_size) + puzzle.box_size):
                    if val in puzzle.get_allowed_values(row, y):
                        cells.append((row, y))

                # If there's only one cell available, it must be where val belongs
                if len(cells) == 1:
                    i, j = cells[0]
                    puzzle.set(i, j, val)
                    num_cells_updated += 1

        return num_cells_updated

    def _solve_two_out_of_three_by_columns(self, puzzle):
        """Take 3 cols at a time, and find digits that are solved in 2 of them."""

        num_cells_updated = 0

        # Take 3 cols at a time (the box size)
        puzzle.box_size = puzzle.box_size
        for y in range(0, puzzle.max_value, puzzle.box_size):
            solved_cells = []
            for j in range(puzzle.box_size):
                solved_cells += puzzle.get_column_values(y + j)

            # Which values appear twice, and therefore missing in 1 row only?
            counter = collections.Counter(solved_cells)
            for val in [v for v in counter.keys() if counter[v] == puzzle.box_size - 1]:
                # Which column is missing the val? Which box?
                cols = set(range(y, y + puzzle.box_size))
                boxes = set(range(puzzle.box_size))
                for j in range(puzzle.box_size):
                    col_values = puzzle.get_column_values(y + j)
                    if val in col_values:
                        cols.remove(y + j)
                        for x in range(puzzle.max_value):
                            if puzzle.get(x, y + j) == val:
                                boxes.remove(x // puzzle.box_size)

                # Lordy. OK, at least now we have 1 column and 3 cells which *could*
                # take the value val. See if there is only 1 cell to put it in

                assert len(cols) == 1
                assert len(boxes) == 1
                (col,) = cols
                (box,) = boxes

                cells = []
                for x in range(box * puzzle.box_size, (box * puzzle.box_size) + puzzle.box_size):
                    if val in puzzle.get_allowed_values(x, col):
                        cells.append((x, col))

                # If there's only one cell available, it must be where val belongs
                if len(cells) == 1:
                    i, j = cells[0]
                    puzzle.set(i, j, val)
                    num_cells_updated += 1

        return num_cells_updated


def _build_sat_clause(max_value, x, y, value):
    """Builds a "clause" that cell(i, j) has value d.

    Args:
        max_value: Dimension of puzzle grid (e.g. 9 for 9x9 puzzle)
        x, y: Row and column
        value: Value that exists at x, y

    Returns:
        An integer, to be interpreted as a clause that is asserting that
        value must exist at position (x, y) in a puzzle of size mv X ,
        """
    ret = (max_value ** 2) * (x - 1) + max_value * (y - 1) + value
    assert ret != 0, f"ret={ret} :: max={max_value}, x,y={(x, y)}, value={value}"
    return ret


@register_solver
class SATSolver:
    """Solves Sudoku puzzle as a Boolean Satisfiability (SAT) problem.

    Credit: http://ilan.schnell-web.net/prog/sudoku/
    This is essentially Schnell's code, where I've changed variable names it
    was part of me understanding how this actually works.

    Relies on pycosat, which in turn relies on PicoSAT.

    Attributes: None
    """

    def solve(self, puzzle):
        """Converts puzzle into an SAT problem, then uses pycosat to solve.

        Args:
            puzzle: A SudokuPuzzle instance.

        Returns:
            True if solved, which it almost always is if the puzzle is valid.
        """
        if puzzle.is_solved():
            return True

        # Locals - accessed by sub-methods below
        mv = puzzle.max_value  # mv: Max Value of a digit in a cell (e.g. 9)
        sz = mv + 1  # sz: Always mv + 1 (e.g. 10), used in range()
        v = _build_sat_clause  # v: Function to build SAT clause

        # Actual solver
        clauses = self.get_sat_clauses(puzzle)
        solset = pycosat.solve(clauses)
        if isinstance(solset, str):
            # Got either "UNSAT" or "UNKNOWN" - either way, we failed
            return False

        # Write solution back into puzzle
        solset = set(solset)

        def read_cell(i, j):
            """Return value of cell(i, j) based on solset"""
            for d in range(1, sz):
                if v(mv, i + 1, j + 1, d) in solset:
                    return d

        for m in puzzle.next_empty_cell():
            puzzle.set(*m, read_cell(*m))

        return puzzle.is_solved()

    def get_sat_clauses(self, puzzle):
        """The SAT clauses are the same for any given puzzle size"""

        # Locals - accessed by sub-methods below
        mv = puzzle.max_value  # mv: Max Value of a digit in a cell
        sz = mv + 1  # sz: Always mv + 1, used in range()
        bs = puzzle.box_size  # bs: Box size (bs * bs == mv)
        v = _build_sat_clause  # v: Function to build SAT clause
        clauses = []  # clauses: List of SAT clauses

        def valid(cells):
            for i, xi in enumerate(cells):
                for j, xj in enumerate(cells):
                    if i < j:
                        for d in range(1, sz):
                            clauses.append(
                                [-v(mv, xi[0], xi[1], d), -v(mv, xj[0], xj[1], d)]
                            )

        # For every cell...
        for i in range(1, sz):
            for j in range(1, sz):
                # Cell must have a value (1 clause)
                clauses.append([v(mv, i, j, d) for d in range(1, sz)])

                # But cannot have two values (number of clauses is equal to the
                # Nth triangle number -- n^2+n / 2, where n=mv-1)
                for d in range(1, sz):
                    for dp in range(d + 1, sz):
                        clauses.append([-v(mv, i, j, d), -v(mv, i, j, dp)])

        # Now ensure every row and column has unique values
        for i in range(1, sz):
            valid([(i, j) for j in range(1, sz)])
            valid([(j, i) for j in range(1, sz)])

        # Now ensure every box has unique values
        for i in range(1, sz, bs):
            for j in range(1, sz, bs):
                valid([(i + k % bs, j + k // bs) for k in range(mv)])

        # For each clue, add a clause asserting that value must exist
        for i in range(mv):
            for j in range(mv):
                d = puzzle.get(i, j)
                if d:
                    clauses.append([v(mv, i + 1, j + 1, d)])

        return clauses


class SudokuSolver:
    """Solves a Sudoku puzzle using the method requested on init.

    The actual solvers are implemented by one of the solver classes. The
    package variable SOLVERS contains the mapping of solver names (labels)
    to classes. The label is the name of the class with the word "Solver"
    removed.

    Attributes:
        method: Method label used on init.
        solver: Instance of the solver class initialized.

    Args:
        method: One of backtracking, constraintpropogation, deductive, or sat.
            Default is constraintpropogation.

    Raises:
        ValueError: If method is not recognized.
    """

    def __init__(self, method="constraintpropogation"):
        super().__init__()
        if method not in SOLVERS:
            raise ValueError(f"Method {method} is not a known Solver class")

        self.method = method
        self.solver = eval(f"SOLVERS['{method}']()")

    def solve(self, puzzle):
        """Solve the SudokuPuzzle using the method requested on init.

        Args:
            puzzle: An unsolved SudokuPuzzle.

        Returns:
            Result of solver's solve() method, which will be True if puzzle
            was solved, False otherwise.
        """
        return self.solver.solve(puzzle)


"""SAMPLE_PUZZLES: Some puzzles for testing, stored as a list of dicts.

Keys:
    level: Difficulty given for a human to solve.
    label: Indicates source and unique label for puzzle.
    link: URL to source for puzzle, where available.
    puzzle: Starting clues encoded as a string.
"""
SAMPLE_PUZZLES = [
    {
        "level": "Kids",
        "label": "SMH 1",
        "puzzle": "89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13",
    },
    {
        "level": "Easy",
        "label": "SMH 2",
        "puzzle": "7438........4.........96....5..8..6.8.47.93.......5........3..99...1.....6....782",
    },
    {
        "level": "Easy",
        "label": "KTH 1",
        "link": "https://www.diva-portal.org/smash/get/diva2:721641/FULLTEXT01.pdf",
        "puzzle": "....37.9263........9...23.587......1.2.9.1.4.9......271.95...7........8636.41....",
    },
    {
        "level": "Easy",
        "label": "Rico Alan Heart",
        "link": "https://www.flickr.com/photos/npcomplete/2304241247/in/photostream/",
        "puzzle": ".216.784.7...1...39.......23.......82.......7.9.....6...4...7.....2.1.......8....",
    },
    {
        "level": "Moderate",
        "label": "SMH 3",
        "puzzle": "..75.....1....98...6..1.43.8.5..2.1.......2...1.7....9..3..8..4.4.9..3..9....6.2.",
    },
    {
        "level": "Hard",
        "label": "SMH 4",
        "puzzle": "..45.7..........98..2.6..3.7..15.........9..........56.86.4.....2....17..3...1...",
    },
    {
        "level": "Hard",
        "label": "SMH 5",
        "puzzle": "..8......1..6..49.5......7..7..4.....5.2.6...8..79..1..63.....1..5.73......9..75.",
    },
    {
        "level": "Hard",
        "label": "Greg [2017]",
        "link": "https://gpicavet.github.io/jekyll/update/2017/12/16/sudoku-solver.html",
        "puzzle": "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 1",
        "link": "https://www.flickr.com/photos/npcomplete/2384354604",
        "puzzle": "9..1.4..2.8..6..7..........4.......1.7.....3.3.......7..........3..7..8.1..2.9..4",
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 2",
        "link": "https://www.flickr.com/photos/npcomplete/2361922697/in/photostream/",
        "puzzle": "1..8.5..4.2..6..9..........8.......6.6.....2.4.......5..........1..9..6.5..4.7..8",
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan Border #1",
        "link": "https://www.flickr.com/photos/npcomplete/2304241257/in/photostream/",
        "puzzle": "..37.26......6....4.......17.......3.4.....1.1.......49.......7....2......68.32..",
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 4",
        "link": "https://www.flickr.com/photos/npcomplete/2361922695/in/photostream/",
        "puzzle": "....25........73........48........597.......238........95........16........83....",
    },
    {
        "level": "Diabolical",
        "label": "Qassim Hamza",
        "link": "https://www.flickr.com/photos/npcomplete/2304537670/in/photostream/",
        "puzzle": "...7..8......4..3......9..16..5......1..3..4...5..1..75..2..6...3..8..9...7.....2",
    },
    {
        "level": "Pathalogical",
        "label": "Rico Alan 3",
        "link": "https://www.flickr.com/photos/npcomplete/2361922699/in/photostream/",
        "puzzle": "..............3.85..1.2.......5.7.....4...1...9.......5......73..2.1........4...9",
    },
    {
        "level": "Pathalogical",
        "label": "World's Hardest Sudoku 2012",
        "link": "https://www.conceptispuzzles.com/index.aspx?uri=info/article/424",
        "puzzle": "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
    },
    {
        "level": "Pathalogical",
        "label": "AI escargot",
        "link": "http://www.aisudoku.com/index_en.html",
        "puzzle": "1....7.9..3..2...8..96..5....53..9...1..8...26....4...3......1..4......7..7...3..",
    },
]
