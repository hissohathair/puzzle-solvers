# sudoku class
#
# Class to manage a Sudoku Puzzle. Only tested with 9x9 puzzle grids.
#

import copy

CAGE_SIZE = 3
MIN_CELL_VALUE = 1
MAX_CELL_VALUE = CAGE_SIZE ** 2
EMPTY_CELL = 0
COMPLETE_SET = set(range(MIN_CELL_VALUE, MAX_CELL_VALUE+1))

def build_empty_grid():
	"""
	Builds a 9x9 matrix, with each cell set to 0
	"""
	ret = [[] for x in range(MAX_CELL_VALUE)]
	for x in range(MAX_CELL_VALUE):
		ret[x] = [0 for y in range(MAX_CELL_VALUE)]

	return ret

def cagenum_to_xy(i):
	"""
	Take the "cages" to be numbered from 0 to 8, starting with 0 in the top left,
	then running left to right and down the rows so that 8 is bottom right. Cage
	0 (0,0)   1 (0, 3)   2 (0, 6)
	3 (3,0)   4 (3, 3)   5 (3, 6)
	6 (6,0)   7 (6, 3)   8 (6, 6)
	"""
	x = (i // 3) * CAGE_SIZE
	y = (i % 3) * CAGE_SIZE
	return [x, y]

def cagexy_to_num(x,y):
	"""
	Given a call at x,y return what the sequential cage number is.
	"""
	cage_x = (x // CAGE_SIZE)
	cage_y = (y // CAGE_SIZE)
	return (cage_x * CAGE_SIZE) + cage_y

class SudokuPuzzle(object):
	def __init__(self, starting_grid=[]):
		"""
		Creates a standard 9x9 puzzle. Will make a copy of the starting_grid
		"""
		if len(starting_grid) == 0:
			self.grid = build_empty_grid()
		else:
			if len(starting_grid) != MAX_CELL_VALUE:
				raise ValueError(f"Unexpected row count {len(starting_grid)} != {MAX_CELL_VALUE}")
			for x in range(MAX_CELL_VALUE):
				if len(starting_grid[x]) != MAX_CELL_VALUE:
					raise ValueError(f"Unexpected column count {len(starting_grid[x])} != {MAX_CELL_VALUE} row {x}")
			self.grid = copy.deepcopy(starting_grid)

		# Cache the list of empty cells
		self.get_all_empty_cells(recalculate=True)

	def get(self, x, y):
		"""
		Returns the cell value at x,y. Returning 0 means no value set.
		"""
		return self.grid[x][y]

	def is_legal(self, x, y, v):
		"""
		Returns true if placing value v at position x,y is legal based on current grid values.
		Might still be an incorrect move, function is only asserting if it looks legal or not.
		Does not actually write value v to x,y -- use set() for that.
		"""

		# Replaying an already played move is allowed
		if self.grid[x][y] == v:
			return True

		# Check that value v is not already in row x, or column y, or cage containing x,y
		return (v not in self.get_row_values(x)) and (v not in self.get_column_values(y)) and (v not in self.get_cage_values(x, y))

	def set(self, x, y, v):
		"""
		Sets the cell at x,y to value v. Will raise an exception if this move is illegal.
		"""
		if v < MIN_CELL_VALUE or v > MAX_CELL_VALUE:
			raise ValueError(f"Value {v} out of range ({MIN_CELL_VALUE}-{MAX_CELL_VALUE})")
		
		if self.is_legal(x, y, v):
			if self.grid[x][y] == EMPTY_CELL:
				self._num_clues += 1
				self._all_empty_cells.remove([x,y])
			self.grid[x][y] = v
		else:
			raise ValueError(f"Value {v} not allowed at {x},{y} (illegal move)")
		return
		
	def clear(self, x, y):
		"""
		Clears the value for a cell at x,y (sets to 0)
		"""
		# OK to "clear" an already empty cell, but it's a no-op
		if self.grid[x][y] != EMPTY_CELL:
			self.grid[x][y] = EMPTY_CELL
			self._num_clues -= 1
			self._all_empty_cells.append([x,y])
			self._all_empty_cells.sort()
		return

	def is_empty(self, x, y):
		"""
		Returns True if the cell is empty (equal to 0)
		"""
		return self.grid[x][y] == EMPTY_CELL

	def num_empty_cells(self, recalculate=False):
		"""
		Return the number of empty cells remaining in the puzzle.
		"""
		if recalculate:
			self.get_all_empty_cells(recalculate=True, return_copy=False)

		return len(self._all_empty_cells)

	def get_all_empty_cells(self, recalculate=False, return_copy=True):
		"""
		Returns a list of 2-tuples that are the position of all empty cells.
		"""
		if recalculate:
			self._all_empty_cells = []
			for x in range(MAX_CELL_VALUE):
				for y in range(MAX_CELL_VALUE):
					if self.is_empty(x, y):
						self._all_empty_cells.append([x, y])
			self._num_clues = (MAX_CELL_VALUE * MAX_CELL_VALUE) - len(self._all_empty_cells)

		if return_copy:
			return copy.deepcopy(self._all_empty_cells)
		else:
			return self._all_empty_cells

	def get_first_empty_cell(self, recalculate=False):
		"""
		Returns the first empty cell that exists in the grid, starting at 0,0
		and searching along the row first. Returns an empty list if there are no empty
		cells.
		"""
		if recalculate:
			ret = self.get_all_empty_cells(recalculate=recalculate)

		if self._all_empty_cells:
			return list(self._all_empty_cells[0])
		else:
			return []

	def get_possible_values(self, x, y):
		"""
		Returns the set of values that are legal for a cell, given the current state of the
		puzzle grid. The values are only legal for the current state. Should never return an
		empty list -- if the cell is not empty will return simply the value placed there.
		"""

		if self.grid[x][y] != EMPTY_CELL:
			return set([self.grid[x][y]])

		# Get the set of all values that are NOT legal because they exist in the row/col/cage
		used_values = set(self.get_row_values(x, include_empty=False) 
						   + self.get_column_values(y, include_empty=False)
						   + self.get_cage_values(x, y, include_empty=False))

		# Set of all possible values for an empty cell is in COMPLETE_SET
		return COMPLETE_SET - used_values

	def get_row_values(self, x, include_empty=True):
		"""
		Return the list of values from row x as a list
		"""
		if include_empty:
			return list(self.grid[x])
		else:
			return [i for i in self.grid[x] if i != EMPTY_CELL]

	def get_column_values(self, y, include_empty=True):
		"""
		Return the list of values from column y as a list
		"""
		if include_empty:
			return [i[y] for i in self.grid]
		else:
			return [i[y] for i in self.grid if i[y] != EMPTY_CELL]

	def get_cage_values(self, x, y, include_empty=True):
		"""
		Return the list of values from the cage containing cell x,y as a list
		"""
		cage_x = (x // CAGE_SIZE) * CAGE_SIZE
		cage_y = (y // CAGE_SIZE) * CAGE_SIZE
		values = [i[cage_y:cage_y+CAGE_SIZE] for i in self.grid[cage_x:cage_x+CAGE_SIZE]]

		if include_empty:
			return [i for sublist in values for i in sublist]
		else:
			return [i for sublist in values for i in sublist if i != EMPTY_CELL ]

	def is_puzzle_valid(self):
		"""
		Returns true if the puzzle is still valid (i.e. obeys the rules). Empty cells are allowed.
		"""

		# Does each row and column contain any repeated values?
		for x in range(MAX_CELL_VALUE):
			values = self.get_row_values(x, include_empty=False)
			if len(values) != len(set(values)):
				return False

		for y in range(MAX_CELL_VALUE):
			values = self.get_column_values(y, include_empty=False)
			if len(values) != len(set(values)):
				return False

		# Does any cage contain repeated values?
		for i in range(MAX_CELL_VALUE):
			pos = cagenum_to_xy(i)
			values = self.get_cage_values(pos[0], pos[1], include_empty=False)
			if len(values) != len(set(values)):
				return False

		return True

	def is_solved(self):
		"""
		Returns true if the puzzle is valid and no empty cells are left.
		"""

		# A solved solution is also valid, and has no empty cells left
		if not self.is_puzzle_valid():
			return False
		if self.num_empty_cells() > 0:
			return False

		# Does each row and column contain all required values and no duplicates?
		looks_valid = True
		for x in range(MAX_CELL_VALUE):
			values = set(self.get_row_values(x))
			if values != COMPLETE_SET:
				looks_valid = False

		for y in range(MAX_CELL_VALUE):
			values = set(self.get_column_values(y))
			if values != COMPLETE_SET:
				looks_valid = False

		# Does each cage have all required values and no duplicates?
		for i in range(MAX_CELL_VALUE):
			pos = cagenum_to_xy(i)
			values = set(self.get_cage_values(pos[0], pos[1]))
			if values != COMPLETE_SET:
				looks_valid = False

		return looks_valid

	def __str__(self):
		return "\n".join(" ".join(map(str, sl)) for sl in self.grid)

	def as_html(self):
		"""
		Renders the current puzzle in simple HTML.
		"""
		data = []
		for x in range(MAX_CELL_VALUE):
			row_to_show = []
			for y in range(MAX_CELL_VALUE):
				if not self.is_empty(x, y):
					row_to_show.append(self.get(x, y))
				else:
					row_to_show.append(' ')
			data.append(row_to_show)

		css_class ="sudoku"
		if self.is_solved():
			css_class += " sudoku-solved"

		ret = '<table class="{}"><tr>{}</tr></table>'.format(css_class, '</tr><tr>'.join('<td>{}</td>'.format('</td><td>'.join(str(_) for _ in row)) for row in data))
		return ret

class SudokuPuzzleConstrained(SudokuPuzzle):
	def __init__(self, starting_grid=[]):
		"""
		Creates the standard puzzle grid (see SudokuPuzzle class), and adds a possibility
		matrix that will act as our Constraint check.
		"""
		super().__init__(starting_grid=starting_grid)
		self.init_contraints()

	def init_contraints(self):
		"""
		Initializes the possible values for each row, each column, and each cage.
		"""
		self.allowed_values_for_row = [COMPLETE_SET - set(self.get_row_values(x, include_empty=False)) for x in range(MAX_CELL_VALUE)]
		self.allowed_values_for_col = [COMPLETE_SET - set(self.get_column_values(y, include_empty=False)) for y in range(MAX_CELL_VALUE)]
		self.allowed_values_for_cage = [COMPLETE_SET - set(self.get_cage_values(cagenum_to_xy(n)[0], cagenum_to_xy(n)[1], include_empty=False)) for n in range(MAX_CELL_VALUE)]
		return
		
	def is_legal(self, x, y, v):
		"""
		Return True if it is legal to write value v to cell x,y.
		Can take advantage of the allowed_values
		"""
		# It's OK to write a value already current
		if self.grid[x][y] == v:
			return True
		return v in self.get_possible_values(x, y)

	def set(self, x, y, v):
		"""
		After setting the value v at position x,y, also updates the possibility matrix to exclude
		the value v from row x, column y, and cage containing x,y. If this leaves any cell with no
		possible values, then raises an exception because the move cannot be valid.
		"""
		# If cell is *already* set, clear it first. Then set it.
		if self.grid[x][y] != EMPTY_CELL:
			self.clear(x, y)
		super().set(x, y, v)

		# Exclude from row x and column y. Don't bother checking to see if it's in the set --
		# if it is NOT then it is an error to write the value to this cell anyway
		self.allowed_values_for_row[x].remove(v)
		self.allowed_values_for_col[y].remove(v)
		self.allowed_values_for_cage[cagexy_to_num(x,y)].remove(v)
		return

	def clear(self, x, y):
		"""
		Clearing is now a bit more complicated. As well as clearing the value from the cell,
		we need to update the possibility matrix with allowed values for the cleared cell,
		and may need to put the value "v" into the possible values for that row, column, or cage.
		"""

		# Is OK to "clear" an empty cell. Otherwise fetch the current value, then call super
		# to clear the cell.
		if self.grid[x][y] == EMPTY_CELL:
			return
		v = self.grid[x][y]
		super().clear(x, y)

		# This value available again for this row, column, and cage
		self.allowed_values_for_row[x].add(v)
		self.allowed_values_for_col[y].add(v)
		self.allowed_values_for_cage[cagexy_to_num(x,y)].add(v)
		return

	def get_possible_values(self, x, y):
		"""
		Returns the current set of possible values at x, y. This is based on the intersection
		of the sets of allowed values for the same row, column and cage. If there is a value
		in the cell, then it is the onlt allowed value.
		"""
		# TODO: This function should be consistent with is_legal()

		if self.grid[x][y] == EMPTY_CELL:
			return self.allowed_values_for_row[x] & self.allowed_values_for_col[y] & self.allowed_values_for_cage[cagexy_to_num(x,y)]
		else:
			return set([self.grid[x][y]])

	def update_using_constraints(self):
		"""
		Loops through all the empty cells and checks what allowed values are possible there. When it
		finds a cell with a single allowed value, will set the cell to that value. Continues until
		there are either no empty cells left, or it's no longer possible to update a cell based on
		single allowed values remaining.

		Returns number of cells updated.
		"""
		num_updated = 1
		total_updated = 0
		while num_updated > 0:
			num_updated = 0
			m = self.get_first_empty_cell()
			if len(m) < 1:
				break
			values = self.get_possible_values(m[0], m[1])
			if len(values) == 1:
				(v,) = values
				self.set(m[0], m[1], v)
				num_updated += 1
			total_updated += num_updated
		return num_updated

	def as_html(self):
		"""
		Renders the current puzzle in simple HTML, showing possible values.
		"""
		data = []
		for x in range(MAX_CELL_VALUE):
			row_to_show = []
			for y in range(MAX_CELL_VALUE):
				if not self.is_empty(x, y):
					row_to_show.append(self.get(x, y))
				elif len(self.possibility_matrix[x][y]) <= 3:
					row_to_show.append(self.possibility_matrix[x][y])
				else:
					row_to_show.append(' ')
			data.append(row_to_show)

		css_class ="sudoku sudoku-possibles"
		if self.is_solved():
			css_class += " sudoku-solved"
			
		ret = '<table class="{}"><tr>{}</tr></table>'.format(css_class, '</tr><tr>'.join('<td>{}</td>'.format('</td><td>'.join(str(_) for _ in row)) for row in data))
		return ret

# Some puzzles for testing
SAMPLE_PUZZLES = [
	{'level': 'Kids',
	 'label': 'SMH 1',
	 'puzzle': [
		    [8, 9, 0, 4, 0, 0, 0, 5, 6],
		    [1, 4, 0, 3, 5, 0, 0, 9, 0],
		    [0, 0, 0, 0, 0, 0, 8, 0, 0],
		    [9, 0, 0, 0, 0, 0, 2, 0, 0],
		    [0, 8, 0, 9, 6, 5, 0, 4, 0],
		    [0, 0, 1, 0, 0, 0, 0, 0, 5],
		    [0, 0, 8, 0, 0, 0, 0, 0, 0],
		    [0, 3, 0, 0, 2, 1, 0, 7, 8],
		    [4, 2, 0, 0, 0, 6, 0, 1, 3]
		]
	},
	{'level': 'Easy',
	  'label': 'SMH 2',
	  'puzzle': [
		    [7, 4, 3, 8, 0, 0, 0, 0, 0],
		    [0, 0, 0, 4, 0, 0, 0, 0, 0],
		    [0, 0, 0, 0, 9, 6, 0, 0, 0],
		    [0, 5, 0, 0, 8, 0, 0, 6, 0],
		    [8, 0, 4, 7, 0, 9, 3, 0, 0],
		    [0, 0, 0, 0, 0, 5, 0, 0, 0],
		    [0, 0, 0, 0, 0, 3, 0, 0, 9],
		    [9, 0, 0, 0, 1, 0, 0, 0, 0],
		    [0, 6, 0, 0, 0, 0, 7, 8, 2]
		]
	},
	 {'level': 'Easy',
	  'label': 'KTH 1',
	  'link': 'https://www.diva-portal.org/smash/get/diva2:721641/FULLTEXT01.pdf',
	  'puzzle': [
	  		[0, 0, 0, 0, 3, 7, 0, 9, 2],
	  		[6, 3, 0, 0, 0, 0, 0, 0, 0],
	  		[0, 9, 0, 0, 0, 2, 3, 0, 5],
	  		[8, 7, 0, 0, 0, 0, 0, 0, 1],
	  		[0, 2, 0, 9, 0, 1, 0, 4, 0],
	  		[9, 0, 0, 0, 0, 0, 0, 2, 7],
	  		[1, 0, 9, 5, 0, 0, 0, 7, 0],
	  		[0, 0, 0, 0, 0, 0, 0, 8, 6],
	  		[3, 6, 0, 4, 1, 0, 0, 0, 0]
	  ]
	 },
	 {'level': 'Easy',
	  'label': 'Rico Alan Heart',
	  'link': 'https://www.flickr.com/photos/npcomplete/2304241247/in/photostream/',
	  'puzzle': [
	  		[0, 2, 1, 6, 0, 7, 8, 4, 0],
	  		[7, 0, 0, 0, 1, 0, 0, 0, 3],
	  		[9, 0, 0, 0, 0, 0, 0, 0, 2],
	  		[3, 0, 0, 0, 0, 0, 0, 0, 8],
	  		[2, 0, 0, 0, 0, 0, 0, 0, 7],
	  		[0, 9, 0, 0, 0, 0, 0, 6, 0],
	  		[0, 0, 4, 0, 0, 0, 7, 0, 0],
	  		[0, 0, 0, 2, 0, 1, 0, 0, 0],
	  		[0, 0, 0, 0, 8, 0, 0, 0, 0]
	  ]
	 },
	{'level': 'Moderate',
	  'label': 'SMH 3',
	  'puzzle': [
		    [0, 0, 7, 5, 0, 0, 0, 0, 0],
		    [1, 0, 0, 0, 0, 9, 8, 0, 0],
		    [0, 6, 0, 0, 1, 0, 4, 3, 0],
		    [8, 0, 5, 0, 0, 2, 0, 1, 0],
		    [0, 0, 0, 0, 0, 0, 2, 0, 0],
		    [0, 1, 0, 7, 0, 0, 0, 0, 9],
		    [0, 0, 3, 0, 0, 8, 0, 0, 4],
		    [0, 4, 0, 9, 0, 0, 3, 0, 0],
		    [9, 0, 0, 0, 0, 6, 0, 2, 0]
		]
	},
	{'level': 'Hard',
	  'label': 'SMH 4',
	  'puzzle': [
		    [0, 0, 4, 5, 0, 7, 0, 0, 0],
		    [0, 0, 0, 0, 0, 0, 0, 9, 8],
		    [0, 0, 2, 0, 6, 0, 0, 3, 0],
		    [7, 0, 0, 1, 5, 0, 0, 0, 0],
		    [0, 0, 0, 0, 0, 9, 0, 0, 0],
		    [0, 0, 0, 0, 0, 0, 0, 5, 6],
		    [0, 8, 6, 0, 4, 0, 0, 0, 0],
		    [0, 2, 0, 0, 0, 0, 1, 7, 0],
		    [0, 3, 0, 0, 0, 1, 0, 0, 0]
		]
	},
	{'level': 'Hard',
	 'label': 'SMH 5',
	 'puzzle': [
		    [0, 0, 8, 0, 0, 0, 0, 0, 0],
		    [1, 0, 0, 6, 0, 0, 4, 9, 0],
		    [5, 0, 0, 0, 0, 0, 0, 7, 0],
		    [0, 7, 0, 0, 4, 0, 0, 0, 0],
		    [0, 5, 0, 2, 0, 6, 0, 0, 0],
		    [8, 0, 0, 7, 9, 0, 0, 1, 0],
		    [0, 6, 3, 0, 0, 0, 0, 0, 1],
		    [0, 0, 5, 0, 7, 3, 0, 0, 0],
		    [0, 0, 0, 9, 0, 0, 7, 5, 0]
	 	]
	},
	{'level': 'Hard',
	 'label': 'Greg [2017]',
	 'link': 'https://gpicavet.github.io/jekyll/update/2017/12/16/sudoku-solver.html',
	 'puzzle': [
	 		[8, 0, 0, 0, 0, 0, 0, 0, 0],
	 		[0, 0, 3, 6, 0, 0, 0, 0, 0],
	 		[0, 7, 0, 0, 9, 0, 2, 0, 0],
	 		[0, 5, 0, 0, 0, 7, 0, 0, 0],
	 		[0, 0, 0, 0, 4, 5, 7, 0, 0],
	 		[0, 0, 0, 1, 0, 0, 0, 3, 0],
	 		[0, 0, 1, 0, 0, 0, 0, 6, 8],
	 		[0, 0, 8, 5, 0, 0, 0, 1, 0],
	 		[0, 9, 0, 0, 0, 0, 4, 0, 0]
	 ]
	},
	{'level': 'Diabolical',
	  'label': 'Rico Alan 1',
	  'link': 'https://www.flickr.com/photos/npcomplete/2384354604',
	  'puzzle': [
		  	[9, 0, 0, 1, 0, 4, 0, 0, 2],
			[0, 8, 0, 0, 6, 0, 0, 7, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[4, 0, 0, 0, 0, 0, 0, 0, 1],
			[0, 7, 0, 0, 0, 0, 0, 3, 0],
			[3, 0, 0, 0, 0, 0, 0, 0, 7],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 3, 0, 0, 7, 0, 0, 8, 0],
			[1, 0, 0, 2, 0, 9, 0, 0, 4]
	  	]
	},
	{'level': 'Diabolical',
	  'label': 'Rico Alan 2',
	  'link': 'https://www.flickr.com/photos/npcomplete/2361922697/in/photostream/',
	  'puzzle': [
		  	[1, 0, 0, 8, 0, 5, 0, 0, 4],
			[0, 2, 0, 0, 6, 0, 0, 9, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[8, 0, 0, 0, 0, 0, 0, 0, 6],
			[0, 6, 0, 0, 0, 0, 0, 2, 0],
			[4, 0, 0, 0, 0, 0, 0, 0, 5],
			[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 9, 0, 0, 6, 0],
			[5, 0, 0, 4, 0, 7, 0, 0, 8]
	  	]
	},
	{'level': 'Diabolical',
	  'label': 'Rico Alan Border #1',
	  'link': 'https://www.flickr.com/photos/npcomplete/2304241257/in/photostream/',
	  'puzzle': [
		    [0, 0, 3, 7, 0, 2, 6, 0, 0],
			[0, 0, 0, 0, 6, 0, 0, 0, 0],
			[4, 0, 0, 0, 0, 0, 0, 0, 1],
			[7, 0, 0, 0, 0, 0, 0, 0, 3],
			[0, 4, 0, 0, 0, 0, 0, 1, 0],
			[1, 0, 0, 0, 0, 0, 0, 0, 4],
			[9, 0, 0, 0, 0, 0, 0, 0, 7],
			[0, 0, 0, 0, 2, 0, 0, 0, 0],
			[0, 0, 6, 8, 0, 3, 2, 0, 0]
		]
	},
	{'level': 'Diabolical',
	  'label': 'Rico Alan 4',
	  'link': 'https://www.flickr.com/photos/npcomplete/2361922695/in/photostream/',
	  'puzzle': [
		  	[0, 0, 0, 0, 2, 5, 0, 0, 0],
			[0, 0, 0, 0, 0, 7, 3, 0, 0],
			[0, 0, 0, 0, 0, 0, 4, 8, 0],
			[0, 0, 0, 0, 0, 0, 0, 5, 9],
			[7, 0, 0, 0, 0, 0, 0, 0, 2],
			[3, 8, 0, 0, 0, 0, 0, 0, 0],
			[0, 9, 5, 0, 0, 0, 0, 0, 0],
			[0, 0, 1, 6, 0, 0, 0, 0, 0],
			[0, 0, 0, 8, 3, 0, 0, 0, 0],
	  	]
	},
	{'level': 'Diabolical',
	  'label': 'Qassim Hamza',
	  'link': 'https://www.flickr.com/photos/npcomplete/2304537670/in/photostream/',
	  'puzzle': [
		  	[0, 0, 0, 7, 0, 0, 8, 0, 0],
			[0, 0, 0, 0, 4, 0, 0, 3, 0],
			[0, 0, 0, 0, 0, 9, 0, 0, 1],
			[6, 0, 0, 5, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 3, 0, 0, 4, 0],
			[0, 0, 5, 0, 0, 1, 0, 0, 7],
			[5, 0, 0, 2, 0, 0, 6, 0, 0],
			[0, 3, 0, 0, 8, 0, 0, 9, 0],
			[0, 0, 7, 0, 0, 0, 0, 0, 2]
	  	]
	},
	{'level': 'Pathalogical',
	  'label': 'Rico Alan 3',
	  'link': 'https://www.flickr.com/photos/npcomplete/2361922699/in/photostream/',
	  'puzzle': [
		  	[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 3, 0, 8, 5],
			[0, 0, 1, 0, 2, 0, 0, 0, 0],
			[0, 0, 0, 5, 0, 7, 0, 0, 0],
			[0, 0, 4, 0, 0, 0, 1, 0, 0],
			[0, 9, 0, 0, 0, 0, 0, 0, 0],
			[5, 0, 0, 0, 0, 0, 0, 7, 3],
			[0, 0, 2, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 0, 4, 0, 0, 0, 9]
	  	]
	},
	{'level': 'Pathalogical',
	  'label': "World's Hardest Sudoku 2012",
	  'link': 'https://www.conceptispuzzles.com/index.aspx?uri=info/article/424',
	  'puzzle': [
		  	[8, 0, 0, 0, 0, 0, 0, 0, 0],
		  	[0, 0, 3, 6, 0, 0, 0, 0, 0],
		  	[0, 7, 0, 0, 9, 0, 2, 0, 0],
		  	[0, 5, 0, 0, 0, 7, 0, 0, 0],
		  	[0, 0, 0, 0, 4, 5, 7, 0, 0],
		  	[0, 0, 0, 1, 0, 0, 0, 3, 0],
		  	[0, 0, 1, 0, 0, 0, 0, 6, 8],
		  	[0, 0, 8, 5, 0, 0, 0, 1, 0],
		  	[0, 9, 0, 0, 0, 0, 4, 0, 0]
	  	]
	},
	{'level': 'Pathalogical',
	  'label': "AI escargot",
	  'link': 'http://www.aisudoku.com/index_en.html',
	  'puzzle': [
		  	[1, 0, 0, 0, 0, 7, 0, 9, 0],
		  	[0, 3, 0, 0, 2, 0, 0, 0, 8],
		  	[0, 0, 9, 6, 0, 0, 5, 0, 0],
		  	[0, 0, 5, 3, 0, 0, 9, 0, 0],
		  	[0, 1, 0, 0, 8, 0, 0, 0, 2],
		  	[6, 0, 0, 0, 0, 4, 0, 0, 0],
		  	[3, 0, 0, 0, 0, 0, 0, 1, 0],
		  	[0, 4, 0, 0, 0, 0, 0, 0, 7],
		  	[0, 0, 7, 0, 0, 0, 3, 0, 0]
	  	]
	},
]

