# puzzlegrid.py
#
# Base class for common 2D constraint-solving puzzle grids (e.g. sudoku; kenken)
#

import copy

DEFAULT_PUZZLE_SIZE = 9
MAX_PUZZLE_SIZE = 25
MIN_PUZZLE_SIZE = 1
EMPTY_CELL = None
MIN_CELL_VALUE = 1

def build_empty_grid(grid_size):
	"""
	Builds a grid_size X grid_size matrix, with each cell set to EMPTY_CELL
	"""
	assert(not EMPTY_CELL)
	assert(grid_size >= MIN_PUZZLE_SIZE)
	ret = [[] for x in range(grid_size)]
	for x in range(grid_size):
		ret[x] = [EMPTY_CELL for y in range(grid_size)]

	return ret

class ConstraintPuzzle(object):
	def __init__(self, grid_size=DEFAULT_PUZZLE_SIZE):
		"""
		Creates a puzzle grid, `grid_size` X `grid_size` (default 9).
		"""
		if grid_size < MIN_PUZZLE_SIZE or grid_size > MAX_PUZZLE_SIZE:
			raise ValueError(f"grid_size={grid_size} outside allowed ranage [{MIN_PUZZLE_SIZE}:{MAX_PUZZLE_SIZE}]")

		# Basic grid
		self._max_cell_value = grid_size
		self._grid = build_empty_grid(grid_size)
		self._num_empty_cells = grid_size * grid_size

		# Initialize constraints
		self._complete_set = set(range(MIN_CELL_VALUE, grid_size+1))
		self._allowed_values_for_row = [set(self._complete_set) for i in range(grid_size)]
		self._allowed_values_for_col = [set(self._complete_set) for i in range(grid_size)]
		return

	def max_value(self):
		"""
		Returns max value for a cell, which is the grid size.
		"""
		return self._max_cell_value

	def init_puzzle(self, starting_grid):
		"""
		Initializes a puzzle grid to the 2D array passed in `grid`. Will clear the current grid.
		Raises ValueError exception if the new starting_grid is the wrong size, or violates a constraint.
		"""
		# First clear the current grid
		for x in range(self._max_cell_value):
			for y in range(self._max_cell_value):
				self.clear(x,y)

		# Check that new grid is correct number of rows
		if len(starting_grid) != self._max_cell_value:
			raise ValueError(f"starting_grid has {len(starting_grid)} rows, exepect {self._max_cell_value}")

		# Check that new grid has correct number of cols
		for x, row in enumerate(starting_grid):
			if len(row) != self._max_cell_value:
				raise ValueError(f"starting_grid row {x} has {len(row)} values, expect {self._max_cell_value}")

			for y, val in enumerate(row):
				if val:
					self.set(x, y, val)
		return

	def num_empty_cells(self):
		"""
		Returns the number of empty cells remaining
		"""
		return self._num_empty_cells

	def num_cells(self):
		"""
		Returns the total number of cells in the grid.
		"""
		return self._max_cell_value * self._max_cell_value

	def get(self, x, y):
		"""
		Returns the cell value at x,y. Returning EMPTY_CELL (None) means no value set. 
		"""
		return self._grid[x][y]

	def set(self, x, y, v):
		"""
		Sets the call at x,y to value v. The set operation must obey the rules of the contraints.
		In this class:
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
		"""
		Clears the value for a cell at x,y
		"""
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

	def is_empty(self, x, y):
		"""
		Returns True if the cell is empty
		"""
		return self._grid[x][y] == EMPTY_CELL

	def find_empty_cell(self):
		"""
		Returns the next empty cell, starting at 0,0 and continuing along the row. Returns
		at the first empty cell found.
		"""
		for i, row in enumerate(self._grid):
			for j, v in enumerate(row):
				if not v:
					return (i, j)
		return ()

	def next_empty_cell(self):
		"""
		Returns the next empty cell that exists in the grid, starting at 0,0 and searching along 
		the row first. Returns an empty tuple at the end of the list.
		"""
		for i, row in enumerate(self._grid):
			for j, v in enumerate(row):
				if not v:
					yield (i, j)
		return ()

	def next_best_empty_cell(self):
		"""
		Generator method that returns the next empty cell with the fewest possible values. 
		Returns an empty tuple when it reaches the end of the list.
		"""
		max_possibilities = 1
		while max_possibilities <= self._max_cell_value:
			for i, row in enumerate(self._grid):
				for j, v in enumerate(row):
					if not v and len(self.get_allowed_values(i,j)) <= max_possibilities:
						yield (i, j)
			max_possibilities += 1
		return ()

	def get_all_empty_cells(self):
		"""
		Convenience method, mainly used in testing. Use generators next_empty_cell or next_best_empty_cell
		instead.
		"""
		return [m for m in self.next_empty_cell()]

	def get_row_values(self, x):
		"""
		Return the list of values from row x as a list (never includes the empty cells)
		"""
		return [i for i in self._grid[x] if i != EMPTY_CELL]

	def get_column_values(self, y):
		"""
		Return the list of values from column y as a list (never includes the empty cells)
		"""
		return [i[y] for i in self._grid if i[y] != EMPTY_CELL]

	def get_allowed_values(self, x, y):
		"""
		Returns the current set of allowed values at x,y. This is based on the intersection
		of the sets of allowed values for the same row and column. If there is already a value in
		a cell, then it is the only allowed value.
		"""
		if self._grid[x][y]:
			return set([self._grid[x][y]])
		else:
			return self._allowed_values_for_row[x] & self._allowed_values_for_col[y]

	def is_allowed_value(self, x, y, v):
		"""
		Returns True if placing value v at position x,y is allowed based on current constraint
		state. The value might still be incorrect, function is only asserting that it is allowed
		based on the current state of the puzzle grid.
		"""
		# Replaying already played move is OK
		if self._grid[x][y] == v:
			return True

		# Check that value v is not already in row x or colum y
		return v in self.get_allowed_values(x, y)

	def is_puzzle_valid(self):
		"""
		This fuction should *always* return True, because it should not be possible to get into an
		invalid state. However since caller clould always access self._grid directly, and since we
		could introduce a bug, this function can perform an additional check.

		Empty cells are allowed -- this is not checking that the puzzle is solved.
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
		"""
		Returns True if there are no empty cells left, and the puzzle is valid.
		"""
		return self.is_puzzle_valid() and self.num_empty_cells() == 0

	def __str__(self):
		blurb = [['-' if v is None else v for v in row] for row in self._grid]
		return "\n".join(" ".join(map(str, sl)) for sl in blurb)
