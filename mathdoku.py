# mathdoku.py
#
# Implement a MathDoku puzzle
#

import puzzlegrid as pg
from functools import reduce
import itertools
import copy
import sys

DEFAULT_GRID_SIZE = 6


# Helper functions


def product(numbers):
    """Return the product of all numbers in list"""
    return reduce(lambda x, y: x * y, numbers)


def subtract(numbers):
    """Return the first number in numbers minus all numbers in list"""
    return reduce(lambda x, y: x - y, numbers)


def divide(numbers):
    """Return the first number in numbers divided by all following numbers"""
    return reduce(lambda x, y: x // y, numbers)


def equals(numbers):
    """Returns the first element in numbers, raises exception if more than 1"""
    if len(numbers) != 1:
        raise ValueError(f"equals only accepts list of length 1")
    return numbers[0]


OPS = {
    '+': sum,
    '-': subtract,
    '/': divide,
    '*': product,
    '=': equals,
}


class MathDoku(pg.ConstraintPuzzle):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, starting_grid=None):
        """We use a different default grid size"""
        super().__init__(grid_size=grid_size, starting_grid=starting_grid)
        return

    def _init_cages(self, cages):
        """Helper method to check and initialise cage list (see init_puzzle)"""
        self._cages = []

        # Copy cages, check they make sense
        for i, cage in enumerate(cages):
            target, operation, num_cells = cage

            # Operation must be valid
            if operation not in OPS.keys():
                raise ValueError(f"Operation {operation} not one of {OPS.keys()}")

            if target < pg.MIN_CELL_VALUE:
                raise ValueError(f"Cage {i} target value {target} < {pg.MIN_CELL_VALUE}")

            # Target should be *possible* assuming the highest value digit can
            # be repeated at most once
            max_target_possible = target
            if operation == '=':
                if num_cells != 1:
                    raise ValueError(f"Assignment in cage {i} must be to a single cell only")
                elif target > self.max_value():
                    raise ValueError(f"Cage {i} assignment of {target} is > {self.max_value()}")

            else:
                if operation in ['+', '*']:
                    possible_digits = [n for n in range(self.max_value(), 1, -1)[0:num_cells - 1]]
                elif operation in ['-', '/']:
                    possible_digits = [n for n in range(1, self.max_value() + 1)[0:num_cells - 1]]
                max_target_possible = OPS[operation]([self.max_value()] + possible_digits)

                if target > max_target_possible:
                    raise ValueError(f"Cage {i} target value {target} exceeds max possible {max_target_possible}")

            # Checks out, can add cage to list
            self._cages.append((target, OPS[operation], num_cells))
        return

    def _init_cage_map(self, cage_map):
        """Helper method to check and init the cage_map (see init_puzzle)"""

        # Cage map should be same dimensions as grid
        if len(cage_map) != self.max_value():
            raise ValueError(f"cage_map has wrong number of rows ({len(cage_map)}, expect {self.max_value()})")
        else:
            for i, row in enumerate(cage_map):
                if len(row) != self.max_value():
                    raise ValueError(f"cage_map row {i} has wrong number of cells ({len(row)}, expect {self.max_value()})")

        # Cage map should map the right number of cells
        cell_counts = [0 for n in self._cages]
        for i in range(self.max_value()):
            for j in range(self.max_value()):
                # print(f"cell({i},{j}) -> {cage_map[i][j]} of {len(self._cages)}", file=sys.stderr)
                if cage_map[i][j] < 0 or cage_map[i][j] >= len(self._cages):
                    raise ValueError(f"Cage ref at ({i},{j}) out of range (0 <= {cage_map[i][j]} <= {len(self._cages)}")
                cell_counts[cage_map[i][j]] += 1

        for i, cage in enumerate(self._cages):
            target, operation, num_cells = cage
            if num_cells != cell_counts[i]:
                raise ValueError(f"Cage {i} expecting {num_cells} but mapped to {cell_counts[i]}")

        # Cage map is OK -- copy it
        self._cells_2_cages = copy.deepcopy(cage_map)

        # Build reverse map now -- cages to list of cells
        self._cages_2_cells = [[] for n in range(len(self._cages))]
        for i in range(self.max_value()):
            for j in range(self.max_value()):
                self._cages_2_cells[self._cells_2_cages[i][j]].append((i, j))

        return

    def init_puzzle(self, cages, cage_map):
        """Initialize a Mathdoku puzzle.

        Mathdoku do not need a starting_grid. Instead they need a list of cages
        and a mapping of cells to their relevant cage.

        Parameters:
        - cages     List of 3-tuples. Each tuple must contain a target number
                    (an int), the target operation (one of +, -, *, or /), and
                    the number of cells contained in the cage. To set a
                    starting clue, which is always a digit in its own cage, use
                    the '=' for operator (e.g. (4, '=', 1))
        - cage_map  A 2D array (list of lists) the same dimensions as
                    starting_grid. Each element has an int between 0 and
                    len(cages) that indicates which cage that cell belongs to.

        The initializer will check that the cell count in cages matches what
        is in cage_map (useful data-entry cross-check).
        """
        self.clear_all()
        self._init_cages(cages)
        self._generate_cage_options()
        self._init_cage_map(cage_map)

        # Final thing we can do -- find the assignment cages and write values
        for i, cage in enumerate(self._cages):
            target, operation, num_cells = cage
            if operation == OPS['=']:
                x, y = self._cages_2_cells[i][0]
                self.set(x, y, target)

        return

    def _generate_cage_options(self):
        """Helper method to generate the list of possible values for a cage"""
        self._cage_possibilities = [[] for n in range(len(self._cages))]
        for i, cage in enumerate(self._cages):
            target, operation, num_cells = cage
            possible_sets = []
            if operation in [OPS['+'], OPS['*']]:
                possible_sets = [x for x in itertools.combinations_with_replacement(self._complete_set, num_cells) if operation(x) == target]
            else:
                possible_sets = [x for x in itertools.product(self._complete_set, repeat=num_cells) if operation(x) == target]
            self._cage_possibilities[i] = possible_sets
        return

    def get_allowed_values(self, x, y):
        """Return set of allowed values at position x,y

        Allowed values is based on what is already set in row x and column y,
        and also based on what is possible inside the cage containing x,y.
        """
        if self.get(x, y):
            return {self.get(x, y)}

        # What's allowed based on row/col?
        allowed_values = super().get_allowed_values(x, y)

        # Which cage is this? What are its options?
        cnum = self._cells_2_cages[x][y]
        possible_sets = self._cage_possibilities[cnum]

        # Flatten to a set
        cage_values = set([i for sublist in possible_sets for i in sublist])
        return allowed_values & cage_values

    def is_puzzle_valid(self):
        """Return True if current puzzle is valid. It may be incomplete"""
        if super().is_puzzle_valid():
            # Rows and cols have no duplicates -- do cages check out?
            for i, cage in enumerate(self._cages):
                target, operation, num_cells = cage
                values = []
                for cell in self._cages_2_cells[i]:
                    x, y = cell
                    if self.get(x, y):
                        values.append(self.get(x, y))

                if len(values) == num_cells:
                    values.sort(reverse=True)
                    if target != operation(values):
                        return False

            return True

        else:
            return False

    def set(self, x, y, v):
        """Sets cell at x,y to value v. Raises exception if puzzle invalid"""

        # First set the value with super
        prev = self.get(x, y)
        super().set(x, y, v)

        # Check if puzzle is still valid
        if not self.is_puzzle_valid():
            if prev:
                super().set(x, y, prev)
            else:
                self.clear(x, y)
            raise ValueError(f"Value {v} violated constraint at {x},{y}")
        return
