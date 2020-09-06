# sudoku class
#
# Class to manage a Sudoku Puzzle. Builds in ConstraintPuzzle
# from puzzlegrid package.
#

import puzzlegrid as pg
import collections

DEFAULT_BOX_SIZE = 3


class SudokuPuzzle(pg.ConstraintPuzzle):
    def __init__(self, box_size=DEFAULT_BOX_SIZE, starting_grid=None):
        """Creates a Sudoku puzzle grid

        The size to pass is the `box_size` which is 3 for the standard 9x9
        puzzle, because the "boxes" are 3x3.
        """
        grid_size = box_size * box_size
        super().__init__(grid_size=grid_size, starting_grid=None)
        self._box_size = box_size

        # Sudoku puzzles have an extra constraint -- boxes cannot contain
        # repeated values
        self._allowed_values_for_box = [
            set(self._complete_set) for i in range(grid_size)
        ]

        # Only when initial constraint sets are initialized can we load the
        # starting grid
        if starting_grid:
            self.init_puzzle(starting_grid)
        return

    def box_size(self):
        """Return box_size"""
        return self._box_size

    def box_num_to_xy(self, i):
        """
        Take the "boxes" to be numbered from 0 to 8, starting with 0 in the top left,
        then running left to right and down the rows so that 8 is bottom right:
        0 (0,0)   1 (0, 3)   2 (0, 6)
        3 (3,0)   4 (3, 3)   5 (3, 6)
        6 (6,0)   7 (6, 3)   8 (6, 6)
        """
        x = (i // 3) * self._box_size
        y = (i % 3) * self._box_size
        return (x, y)

    def box_xy_to_num(self, x, y):
        """
        Given a call at x,y return what the sequential box number is.
        """
        box_x = x // self._box_size
        box_y = y // self._box_size
        return (box_x * self._box_size) + box_y

    def set(self, x, y, v):
        """
        Calls the parent (ConstraintPuzzle) set method first, then updates our additional
        box constraint.
        """
        if self._grid[x][y] == v:
            return
        super().set(x, y, v)

        # Update box constraints
        self._allowed_values_for_box[self.box_xy_to_num(x, y)].remove(v)
        return

    def clear(self, x, y):
        """
        Clears the value at x,y. Will update the box constraints.
        """
        if not self._grid[x][y]:
            return

        # Stash previous value, then clear cell
        prev = self._grid[x][y]
        super().clear(x, y)

        # This value available again for this box
        self._allowed_values_for_box[self.box_xy_to_num(x, y)].add(prev)
        return

    def get_box_values(self, x, y):
        """
        Return the list of values from the box containing cell x,y as a list.
        """
        box_x = (x // self._box_size) * self._box_size
        box_y = (y // self._box_size) * self._box_size
        values = [
            i[box_y:box_y + self._box_size]
            for i in self._grid[box_x:box_x + self._box_size]
        ]
        return [i for sublist in values for i in sublist if i]

    def get_allowed_values(self, x, y):
        """
        Returns the current set of possible values at x, y. This is based on the intersection
        of the sets of allowed values for the same row, column and box. If there is a value
        in the cell, then it is the only allowed value.
        """
        if self._grid[x][y]:
            return set([self._grid[x][y]])
        else:
            return super().get_allowed_values(x, y) & self._allowed_values_for_box[self.box_xy_to_num(x, y)]

    def is_puzzle_valid(self):
        """
        Returns True if the puzzle is still valid (i.e. obeys the rules). Empty cells are allowed.
        We only need to check the box constraint (parent class does rows and columns already).
        This method should *always* return True, since it should not be possible to put a puzzle
        into an invalid state (not without accessing self._grid directly...)
        """
        # Does any box contain repeated values?
        for i in range(self._max_cell_value):
            pos = self.box_num_to_xy(i)
            values = self.get_box_values(*pos)
            if len(values) != len(set(values)):
                return False

        return super().is_puzzle_valid()

    def as_html(self, show_possibilities=0):
        """
        Renders the current puzzle in simple HTML. If show_possibilities > 0, then cells
        with fewer possible values than that will show the possible values.
        """
        data = []
        for x in range(self._max_cell_value):
            row_to_show = []
            for y in range(self._max_cell_value):
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


SOLVERS = dict()


def register_solver(cls):
    """Register method as a solver"""
    idx = cls.__name__.replace('Solver', '').lower()
    SOLVERS[idx] = cls
    return cls


@register_solver
class BacktrackingSolver(pg.ConstraintSolver):
    """Solve a Sudoku puzzle using backtracking"""

    def solve(self, puzzle):
        """Solve the puzzle

        Should always return True (backtracking always works...eventually).
        Will raise an exception if an already solved puzzle is passed
        """
        assert(not puzzle.is_solved())
        self.max_depth = 0
        self.backtrack_count = 0
        return self._solve_backtracking(puzzle)

    def _solve_backtracking(self, puzzle, depth=0):
        """Internal method called recursively"""

        if puzzle.num_empty_cells() == 0:
            return True

        if depth > self.max_depth:
            self.max_depth = depth

        x, y = puzzle.find_empty_cell()
        for val in puzzle.get_allowed_values(x, y):
            puzzle.set(x, y, val)
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
    """

    def _solve_backtracking(self, puzzle, depth=0):
        """Internal method called recursively"""

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
            return True

        for val in puzzle.get_allowed_values(x, y):
            puzzle.set(x, y, val)
            if self._solve_backtracking(puzzle, depth=depth + 1):
                return True
            else:
                puzzle.clear(x, y)
                self.backtrack_count += 1

        return False


@register_solver
class SinglePossibilitiesSolver(pg.ConstraintSolver):
    """Attempt to solve the puzzle by finding cells with single possibilities"""

    def solve(self, puzzle):
        """Solve the puzzle. Return True if solved, False otherwise.

        This method can only solve very simple puzzles on its own.
        """
        assert(not puzzle.is_solved())
        return self._solve_single_possibilities(puzzle)

    def _solve_single_possibilities(self, puzzle):
        """
        Single possibilities are those cells for which there is only one
        possible value, all others already exist in that row, column or box.
        This is sometimes enough to solve very easy Sudoku puzzles.

        Returns True if the puzzle is solved, False otherwise.
        """

        # Keeps trying until we are no longer able to solve cells
        num_cells_updated = 1
        while num_cells_updated > 0:
            num_cells_updated = 0
            for m in puzzle.next_best_empty_cell():
                possibles = puzzle.get_allowed_values(*m)
                if len(possibles) == 1:
                    (v,) = possibles
                    puzzle.set(*m, v)
                    num_cells_updated += 1

        return puzzle.is_solved()


@register_solver
class OnlySquaresSolver(pg.ConstraintSolver):
    """Attempt to solve the puzzle by finding values that have only one possible
    cell location that they can go into."""

    def solve(self, puzzle):
        """Solve the puzzle. Return True if solved, False otherwise.

        This method can solve easy to intermediate puzzles on its own, but
        will struggle with hard or difficult puzzles.
        """

        # A group is a row, column, or box. Calls the group-specific methods below.
        # Keeps trying until the method fails to solve any new cells
        num_cells_updated = 1
        while num_cells_updated > 0:
            num_cells_updated = self.solve_only_row_squares(puzzle) + self.solve_only_column_squares(puzzle) + self.solve_only_box_squares(puzzle)

        return puzzle.is_solved()

    def solve_only_row_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the row

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for x in range(puzzle.max_value()):
            # What hasn't this row got?
            missing = puzzle.complete_set() - set(puzzle.get_row_values(x))

            # How many places on this row could each missing value go?
            for v in missing:
                possible_cells = []
                for y in range(puzzle.max_value()):
                    if puzzle.is_empty(x, y) and v in puzzle.get_allowed_values(x, y):
                        possible_cells.append((x, y))

                # only one possible location?
                if len(possible_cells) == 1:
                    # print(f"Row {x} needs a {v} and it can only go here {possible_cells}", file=sys.stderr)
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], v)

        return num_cells_updated

    def solve_only_column_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the column

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for y in range(puzzle.max_value()):
            # What hasn't this column got?
            missing = puzzle.complete_set() - set(puzzle.get_column_values(y))

            # How many places in this column could each missing value go?
            for v in missing:
                possible_cells = []
                for x in range(puzzle.max_value()):
                    if puzzle.is_empty(x, y) and v in puzzle.get_allowed_values(x, y):
                        possible_cells.append((x, y))

                # Only one possible location?
                if len(possible_cells) == 1:
                    # print(f"Column {y} needs a {v} and it can only go here {possible_cells}", file=sys.stderr)
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], v)

        return num_cells_updated

    def solve_only_box_squares(self, puzzle):
        """Find cases where there is only one cell that can take a particular
        value for the box

        Returns number of cells solved this call.
        """
        num_cells_updated = 0
        for box in range(puzzle.max_value()):
            # What hasn't this box got?
            missing = puzzle.complete_set() - set(puzzle.get_box_values(*puzzle.box_num_to_xy(box)))

            # How many places in this box could each missing value go?
            for v in missing:
                possible_cells = []
                box_x, box_y = puzzle.box_num_to_xy(box)
                for x in range(box_x, box_x + puzzle.box_size()):
                    for y in range(box_y, box_y + puzzle.box_size()):
                        if puzzle.is_empty(x, y) and v in puzzle.get_allowed_values(x, y):
                            possible_cells.append((x, y))

                # Only one possible location?
                if len(possible_cells) == 1:
                    # print(f"Box {box} needs a {v} and it can only go here {possible_cells}", file=sys.stderr)
                    num_cells_updated += 1
                    puzzle.set(*possible_cells[0], v)

        return num_cells_updated


@register_solver
class TwoOutofThreeSolver(pg.ConstraintSolver):
    """Attempt to solve cells using the "two out of three" strategy"""

    def solve(self, puzzle):
        """Attempt to solve, returning True if puzzle solved."""
        num_cells_updated = 1
        while num_cells_updated > 0:
            num_cells_updated = self.solve_two_out_of_three_by_rows(puzzle) + self.solve_two_out_of_three_by_columns(puzzle)
        return puzzle.is_solved()

    def solve_two_out_of_three_by_rows(self, puzzle):
        """Take 3 rows at a time, and find digits that are solved in 2 of
        them. This narrows down to the third row, and one box.
        """
        num_cells_updated = 0

        # Take 3 rows at a time (the box size)
        bs = puzzle.box_size()
        for x in range(0, puzzle.max_value(), bs):
            solved_cells = []
            for i in range(bs):
                solved_cells += puzzle.get_row_values(x + i)

            # Which values appear twice, and therefore missing in 1 row only?
            counter = collections.Counter(solved_cells)
            for val in [x for x in counter.keys() if counter[x] == bs - 1]:
                # Which row is missing the val? Which box?
                rows = set(range(x, x + bs))
                boxes = set(range(bs))
                for i in range(bs):
                    row_values = puzzle.get_row_values(x + i)
                    if val in row_values:
                        rows.remove(x + i)
                        for y in range(puzzle.max_value()):
                            if puzzle.get(x + i, y) == val:
                                boxes.remove(y // bs)

                # Lordy. OK, at least now we have 1 row and 3 cells which *could*
                # take the value val. See if there is only 1 cell to put it in
                assert(len(rows) == 1)
                assert(len(boxes) == 1)
                row, = rows
                box, = boxes
                cells = []
                for y in range(box * bs, (box * bs) + bs):
                    if puzzle.is_allowed_value(row, y, val):
                        cells.append((row, y))

                # If there's only one cell available, it must be where val belongs
                if len(cells) == 1:
                    i, j = cells[0]
                    puzzle.set(i, j, val)
                    num_cells_updated += 1

                # print(f"{val} in 2/3 rows from {x}-{x+2} missing from {rows} must be in {cells}")

        return num_cells_updated

    def solve_two_out_of_three_by_columns(self, puzzle):
        """Take 3 cols at a time, and find digits that are solved in 2 of
        them. This narrows down to the third row, and one box.
        """
        num_cells_updated = 0

        # Take 3 cols at a time (the box size)
        bs = puzzle.box_size()
        for y in range(0, puzzle.max_value(), bs):
            solved_cells = []
            for j in range(bs):
                solved_cells += puzzle.get_column_values(y + j)

            # Which values appear twice, and therefore missing in 1 row only?
            counter = collections.Counter(solved_cells)
            for val in [v for v in counter.keys() if counter[v] == bs - 1]:
                # Which column is missing the val? Which box?
                cols = set(range(y, y + bs))
                boxes = set(range(bs))
                for j in range(bs):
                    col_values = puzzle.get_column_values(y + j)
                    if val in col_values:
                        cols.remove(y + j)
                        for x in range(puzzle.max_value()):
                            if puzzle.get(x, y + j) == val:
                                boxes.remove(x // bs)

                # Lordy. OK, at least now we have 1 column and 3 cells which *could*
                # take the value val. See if there is only 1 cell to put it in
                assert(len(cols) == 1)
                assert(len(boxes) == 1)
                col, = cols
                box, = boxes
                cells = []
                for x in range(box * bs, (box * bs) + bs):
                    if puzzle.is_allowed_value(x, col, val):
                        cells.append((x, col))

                # If there's only one cell available, it must be where val belongs
                if len(cells) == 1:
                    i, j = cells[0]
                    puzzle.set(i, j, val)
                    num_cells_updated += 1

                # print(f"{val} in 2/3 cols from {y}-{y+2} missing from {cols} must be in {cells}")

        return num_cells_updated


@register_solver
class CombinationSolver(ConstraintPropogationSolver):
    """Solves a Sudoku puzzle using a combination of deductive logic and
    backtracking with constraint propogation."""

    def __init__(self, use_backtracking=True):
        self.use_backtracking = use_backtracking
        return

    def solve(self, puzzle):
        """Try single possibilities first, then constraint propogation"""
        self.deductive_loops = 0

        # Two deductive solver classes
        slv1 = SinglePossibilitiesSolver()
        slv2 = OnlySquaresSolver()
        slv3 = TwoOutofThreeSolver()

        # Keep trying the deductive logic until they stop updating cells
        num_cells_updated = 1
        while num_cells_updated > 0:
            self.deductive_loops += 1
            num_cells_updated = 0
            num_empty_cells = puzzle.num_empty_cells()

            if slv1.solve(puzzle):
                return True
            elif slv2.solve(puzzle):
                return True
            elif slv3.solve(puzzle):
                return True

            num_cells_updated = num_empty_cells - puzzle.num_empty_cells()

        # Dropped out of the loop, so puzzle not solved -- fall back to CP
        if self.use_backtracking:
            return super().solve(puzzle)
        else:
            return puzzle.is_solved()


class SudokuSolver(pg.ConstraintSolver):
    """Solves a Sudoku puzzle using some method implemented by one of the solver
    classes"""

    def __init__(self, method="backtracking"):
        super().__init__()
        if method not in SOLVERS:
            raise ValueError(f"Method {method} is not a known Solver class")

        self.solver = eval(f"SOLVERS['{method}']()")
        return

    def solve(self, puzzle):
        return self.solver.solve(puzzle)


# Some puzzles for testing
SAMPLE_PUZZLES = [
    {
        "level": "Kids",
        "label": "SMH 1",
        "puzzle": [
            [8, 9, 0, 4, 0, 0, 0, 5, 6],
            [1, 4, 0, 3, 5, 0, 0, 9, 0],
            [0, 0, 0, 0, 0, 0, 8, 0, 0],
            [9, 0, 0, 0, 0, 0, 2, 0, 0],
            [0, 8, 0, 9, 6, 5, 0, 4, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 5],
            [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 2, 1, 0, 7, 8],
            [4, 2, 0, 0, 0, 6, 0, 1, 3],
        ],
    },
    {
        "level": "Easy",
        "label": "SMH 2",
        "puzzle": [
            [7, 4, 3, 8, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 9, 6, 0, 0, 0],
            [0, 5, 0, 0, 8, 0, 0, 6, 0],
            [8, 0, 4, 7, 0, 9, 3, 0, 0],
            [0, 0, 0, 0, 0, 5, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 0, 9],
            [9, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 6, 0, 0, 0, 0, 7, 8, 2],
        ],
    },
    {
        "level": "Easy",
        "label": "KTH 1",
        "link": "https://www.diva-portal.org/smash/get/diva2:721641/FULLTEXT01.pdf",
        "puzzle": [
            [0, 0, 0, 0, 3, 7, 0, 9, 2],
            [6, 3, 0, 0, 0, 0, 0, 0, 0],
            [0, 9, 0, 0, 0, 2, 3, 0, 5],
            [8, 7, 0, 0, 0, 0, 0, 0, 1],
            [0, 2, 0, 9, 0, 1, 0, 4, 0],
            [9, 0, 0, 0, 0, 0, 0, 2, 7],
            [1, 0, 9, 5, 0, 0, 0, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 8, 6],
            [3, 6, 0, 4, 1, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Easy",
        "label": "Rico Alan Heart",
        "link": "https://www.flickr.com/photos/npcomplete/2304241247/in/photostream/",
        "puzzle": [
            [0, 2, 1, 6, 0, 7, 8, 4, 0],
            [7, 0, 0, 0, 1, 0, 0, 0, 3],
            [9, 0, 0, 0, 0, 0, 0, 0, 2],
            [3, 0, 0, 0, 0, 0, 0, 0, 8],
            [2, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 9, 0, 0, 0, 0, 0, 6, 0],
            [0, 0, 4, 0, 0, 0, 7, 0, 0],
            [0, 0, 0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 8, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Moderate",
        "label": "SMH 3",
        "puzzle": [
            [0, 0, 7, 5, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 9, 8, 0, 0],
            [0, 6, 0, 0, 1, 0, 4, 3, 0],
            [8, 0, 5, 0, 0, 2, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 0],
            [0, 1, 0, 7, 0, 0, 0, 0, 9],
            [0, 0, 3, 0, 0, 8, 0, 0, 4],
            [0, 4, 0, 9, 0, 0, 3, 0, 0],
            [9, 0, 0, 0, 0, 6, 0, 2, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "SMH 4",
        "puzzle": [
            [0, 0, 4, 5, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 9, 8],
            [0, 0, 2, 0, 6, 0, 0, 3, 0],
            [7, 0, 0, 1, 5, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 5, 6],
            [0, 8, 6, 0, 4, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 1, 7, 0],
            [0, 3, 0, 0, 0, 1, 0, 0, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "SMH 5",
        "puzzle": [
            [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 6, 0, 0, 4, 9, 0],
            [5, 0, 0, 0, 0, 0, 0, 7, 0],
            [0, 7, 0, 0, 4, 0, 0, 0, 0],
            [0, 5, 0, 2, 0, 6, 0, 0, 0],
            [8, 0, 0, 7, 9, 0, 0, 1, 0],
            [0, 6, 3, 0, 0, 0, 0, 0, 1],
            [0, 0, 5, 0, 7, 3, 0, 0, 0],
            [0, 0, 0, 9, 0, 0, 7, 5, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "Greg [2017]",
        "link": "https://gpicavet.github.io/jekyll/update/2017/12/16/sudoku-solver.html",
        "puzzle": [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 1",
        "link": "https://www.flickr.com/photos/npcomplete/2384354604",
        "puzzle": [
            [9, 0, 0, 1, 0, 4, 0, 0, 2],
            [0, 8, 0, 0, 6, 0, 0, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 7, 0, 0, 0, 0, 0, 3, 0],
            [3, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 7, 0, 0, 8, 0],
            [1, 0, 0, 2, 0, 9, 0, 0, 4],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 2",
        "link": "https://www.flickr.com/photos/npcomplete/2361922697/in/photostream/",
        "puzzle": [
            [1, 0, 0, 8, 0, 5, 0, 0, 4],
            [0, 2, 0, 0, 6, 0, 0, 9, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 0, 0, 0, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 0, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 5],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 9, 0, 0, 6, 0],
            [5, 0, 0, 4, 0, 7, 0, 0, 8],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan Border #1",
        "link": "https://www.flickr.com/photos/npcomplete/2304241257/in/photostream/",
        "puzzle": [
            [0, 0, 3, 7, 0, 2, 6, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 1],
            [7, 0, 0, 0, 0, 0, 0, 0, 3],
            [0, 4, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 4],
            [9, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 6, 8, 0, 3, 2, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 4",
        "link": "https://www.flickr.com/photos/npcomplete/2361922695/in/photostream/",
        "puzzle": [
            [0, 0, 0, 0, 2, 5, 0, 0, 0],
            [0, 0, 0, 0, 0, 7, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 4, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 5, 9],
            [7, 0, 0, 0, 0, 0, 0, 0, 2],
            [3, 8, 0, 0, 0, 0, 0, 0, 0],
            [0, 9, 5, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 6, 0, 0, 0, 0, 0],
            [0, 0, 0, 8, 3, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Qassim Hamza",
        "link": "https://www.flickr.com/photos/npcomplete/2304537670/in/photostream/",
        "puzzle": [
            [0, 0, 0, 7, 0, 0, 8, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 9, 0, 0, 1],
            [6, 0, 0, 5, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 3, 0, 0, 4, 0],
            [0, 0, 5, 0, 0, 1, 0, 0, 7],
            [5, 0, 0, 2, 0, 0, 6, 0, 0],
            [0, 3, 0, 0, 8, 0, 0, 9, 0],
            [0, 0, 7, 0, 0, 0, 0, 0, 2],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "Rico Alan 3",
        "link": "https://www.flickr.com/photos/npcomplete/2361922699/in/photostream/",
        "puzzle": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 8, 5],
            [0, 0, 1, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 5, 0, 7, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 1, 0, 0],
            [0, 9, 0, 0, 0, 0, 0, 0, 0],
            [5, 0, 0, 0, 0, 0, 0, 7, 3],
            [0, 0, 2, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 9],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "World's Hardest Sudoku 2012",
        "link": "https://www.conceptispuzzles.com/index.aspx?uri=info/article/424",
        "puzzle": [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "AI escargot",
        "link": "http://www.aisudoku.com/index_en.html",
        "puzzle": [
            [1, 0, 0, 0, 0, 7, 0, 9, 0],
            [0, 3, 0, 0, 2, 0, 0, 0, 8],
            [0, 0, 9, 6, 0, 0, 5, 0, 0],
            [0, 0, 5, 3, 0, 0, 9, 0, 0],
            [0, 1, 0, 0, 8, 0, 0, 0, 2],
            [6, 0, 0, 0, 0, 4, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 4, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 7, 0, 0, 0, 3, 0, 0],
        ],
    },
]
