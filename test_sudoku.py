# test

import unittest
import sudoku

TEST_PUZZLE =[
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

SOLVED_PUZZLE = [
	[8, 9, 3, 4, 7, 2, 1, 5, 6],
	[1, 4, 6, 3, 5, 8, 7, 9, 2],
	[2, 7, 5, 6, 1, 9, 8, 3, 4],
	[9, 5, 4, 1, 8, 3, 2, 6, 7],
	[7, 8, 2, 9, 6, 5, 3, 4, 1],
	[3, 6, 1, 2, 4, 7, 9, 8, 5],
	[5, 1, 8, 7, 3, 4, 6, 2, 9],
	[6, 3, 9, 5, 2, 1, 4, 7, 8],
	[4, 2, 7, 8, 9, 6, 5, 1, 3]
 ]

LEGAL_MOVES = [
			[0, 2, 3], [3, 3, 1], [4, 4, 6], [1, 6, 7], [7, 3, 5], [1, 8, 2],
			[8, 2, 7], [8, 6, 5], [5, 0, 3], [5, 7, 8], [6, 4, 3]
		]
ILLEGAL_MOVES = [
			[0, 2, 8], [0, 2, 1], [3, 3, 2], [3, 3, 4], [2, 2, 4], [3, 3, 6],
			[0, 0, 9], [0, 0, 1], [2, 2, 4], [2, 3, 4]
		]

class TestFunctions(unittest.TestCase):
	def test_cagenum_toxy(self):
		"""
		0 (0,0)   1 (0, 3)   2 (0, 6)
		3 (3,0)   4 (3, 3)   5 (3, 6)
		6 (6,0)   7 (6, 3)   8 (6, 6)
		"""
		correct_values = [[0,0], [0,3], [0,6], 
						  [3,0], [3,3], [3,6],
						  [6,0], [6,3], [6,6]]
		for i in range(sudoku.MAX_CELL_VALUE):
			with self.subTest(f"Cage {i} at {correct_values[i]}"):
				self.assertEqual(sudoku.cagenum_to_xy(i), correct_values[i])
				self.assertEqual(sudoku.cagexy_to_num(correct_values[i][0], correct_values[i][1]), i)
	return

	def test_cagexy_tonum(self):
		for x in range(sudoku.MAX_CELL_VALUE):
			for y in range(sudoku.MAX_CELL_VALUE):
				with self.subTest(f"Cage for {x},{y}"):
					num = sudoku.cagexy_to_num(x, y)
					pos = sudoku.cagenum_to_xy(num)
					self.assertEqual(sudoku.cagexy_to_num(x,y), sudoku.cagexy_to_num(pos[0],pos[1]))
	return

	def test_count_clues(self):
	# Test data
	self.assertEqual(TEST_CLUES, sudoku.count_clues(TEST_PUZZLE))

	# Manually calculated and stored in SAMPLE_PUZZLES
	for sample in sudoku.SAMPLE_PUZZLES:
		if 'clues' in sample:
			self.assertEqual(sample['clues'], sudoku.count_clues(sample['puzzle']))
	return

class TestSudoku(unittest.TestCase):
	def setUp(self):
		self.p = sudoku.SudokuPuzzle(TEST_PUZZLE)
		self.s = sudoku.SudokuPuzzle(SOLVED_PUZZLE)
		self.legal_moves = LEGAL_MOVES
		self.illegal_moves = ILLEGAL_MOVES

	def test_class_init(self):
		"""
		Test that class init makes a copy of starting grid
		"""
		x = 0
		y = 2
		test_value = TEST_PUZZLE[x][y]
		set_value  = 3
		self.assertNotEqual(test_value, set_value) # test data error

		self.p.set(0, 0, set_value)
		self.assertEqual(self.p.get(0, 0), set_value)
		self.assertNotEqual(self.p.get(0, 0), test_value)

	def test_class_init_empty(self):
		"""
		Test that class init can create an empty grid
		"""
		p = sudoku.SudokuPuzzle()
		for x in range(sudoku.MAX_CELL_VALUE):
			for y in range(sudoku.MAX_CELL_VALUE):
				self.assertEqual(p.get(x, y), sudoku.EMPTY_CELL)

		self.assertEqual(p.find_empty_cell(), (0,0))
		self.assertEqual(len(p.get_all_empty_cells()), sudoku.MAX_CELL_VALUE ** 2)

	def test_class_init_raises_exception(self):
		"""
		Test that class init raises an exception for malformed grids
		"""
		data = [1, 2, 3]
		self.assertRaises(ValueError, sudoku.SudokuPuzzle, data)
		data = [[1, 2, 3] for x in range(sudoku.MAX_CELL_VALUE) ]
		self.assertRaises(ValueError, sudoku.SudokuPuzzle, data)

	def test_clear_and_set(self):
		"""
		Correctly clear and set a.get value
		"""
		x = 1
		y = 1
		test_value = TEST_PUZZLE[x][y]
		self.assertNotEqual(test_value, sudoku.EMPTY_CELL) # test data error

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

	def test_empty_cells(self):
		"""
		Check the methods for getting empty cells
		"""
		with self.subTest(f"Basic empty cell count check"):
			self.assertEqual(len(self.p.get_all_empty_cells()), 50)
			self.assertEqual(len(self.s.get_all_empty_cells()), 0)

		with self.subTest(f"Empty cells are empty"):
			for m in self.p.get_all_empty_cells():
				self.assertEqual(self.p.get(m[0], m[1]), sudoku.EMPTY_CELL)

		with self.subTest(f"find_empty_cell returns all empty cells"):
			mts = self.p.get_all_empty_cells()
			for i, mt in enumerate(mts):
				m = self.p.find_empty_cell()
				self.assertEqual(self.p.get(m[0], m[1]), sudoku.EMPTY_CELL)
				self.assertEqual(mt, m)
				self.p.set(m[0], m[1], self.s.get(m[0], m[1]))
			self.assertEqual(self.p.num_empty_cells(), 0)

		return

	def test_next_empty_cell(self):
		"""
		Test generator function next_empty_cell()
		"""
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
		with self.subTest("get_row_values"):
			self.assertEqual(self.p.get_row_values(0, include_empty=True), [8, 9, 0, 4, 0, 0, 0, 5, 6])
			self.assertEqual(self.p.get_row_values(0, include_empty=False), [8, 9, 4, 5, 6])
			self.assertEqual(self.p.get_row_values(7, include_empty=True), [0, 3, 0, 0, 2, 1, 0, 7, 8])
			self.assertEqual(self.p.get_row_values(7, include_empty=False), [3, 2, 1, 7, 8])

		with self.subTest("get_column_values"):
			self.assertEqual(self.p.get_column_values(0, include_empty=True), [8, 1, 0, 9, 0, 0, 0, 0, 4])
			self.assertEqual(self.p.get_column_values(0, include_empty=False), [8, 1, 9, 4])
			self.assertEqual(self.p.get_column_values(7, include_empty=True), [5, 9, 0, 0, 4, 0, 0, 7, 1])
			self.assertEqual(self.p.get_column_values(7, include_empty=False), [5, 9, 4, 7, 1])

		with self.subTest("get_cage_values"):
			self.assertEqual(self.p.get_cage_values(0, 0, include_empty=True), [8, 9, 0, 1, 4, 0, 0, 0, 0])
			self.assertEqual(self.p.get_cage_values(0, 0, include_empty=False), [8, 9, 1, 4])
			self.assertEqual(self.p.get_cage_values(7, 0, include_empty=True), [0, 0, 8, 0, 3, 0, 4, 2, 0])
			self.assertEqual(self.p.get_cage_values(7, 0, include_empty=False), [8, 3, 4, 2])
			self.assertEqual(self.p.get_cage_values(7, 7, include_empty=True), [0, 0, 0, 0, 7, 8, 0, 1, 3])
			self.assertEqual(self.p.get_cage_values(7, 7, include_empty=False), [7, 8, 1, 3])

	def test_possible_values(self):
		"""
		Test that function returns legal values 
		"""
		with self.subTest("Checking possible values"):
			self.assertEqual(self.p.get_possible_values(0, 0), {8})
			self.assertEqual(self.p.get_possible_values(2, 2), {2, 3, 5, 6, 7})
			self.assertEqual(self.p.get_possible_values(7, 0), {5, 6})

		with self.subTest("Possible values are legal"):
			for x in range(sudoku.MAX_CELL_VALUE):
				for y in range(sudoku.MAX_CELL_VALUE):
					with self.subTest(f"Cell {x},{y}"):
						vlist = self.p.get_possible_values(x,y)
						if self.p.is_empty(x, y):
							self.assertTrue(len(vlist) >= 1)
						else:
							self.assertTrue(len(vlist) == 1)

						with self.subTest(f"Cell {x},{y} -> {vlist}"):
							for v in vlist:
								self.assertTrue(self.p.is_legal_value(x, y, v))

	def test_legal_move(self):
		"""
		Correctly tell us if a move is legal
		"""
		for i in range(len(self.legal_moves)):
			with self.subTest(i=i):
				m = self.legal_moves[i]
				self.assertEqual(SOLVED_PUZZLE[m[0]][m[1]], m[2])  # test data error
				self.assertTrue(self.p.is_legal_value(m[0], m[1], m[2]))

	def test_invalid_move(self):
		"""
		Correctly tell us if we use a value out of range for a cell
		"""
		self.assertRaises(ValueError, self.p.set, 0, 0, 0)
		self.assertRaises(ValueError, self.p.set, 0, 0, sudoku.MAX_CELL_VALUE+1)

	def test_illegal_moves(self):
		"""
		Correctly tell us if a move is NOT legal
		"""
		for i in range(len(self.illegal_moves)):
			with self.subTest(i=i):
				m = self.illegal_moves[i]
				self.assertFalse(self.p.is_legal_value(m[0], m[1], m[2]))

	def test_illegal_set(self):
		"""
		Throw exception if we attempt an illegal move
		"""
		for i in range(len(self.illegal_moves)):
			with self.subTest(i=i):
				m = self.illegal_moves[i]
				self.assertRaises(ValueError, self.p.set, m[0], m[1], m[2])

	def test_is_puzzle_valid(self):
		"""
		Correctly tell us if a puzzle grid is or is not valid
		"""
		self.assertTrue(self.p.is_puzzle_valid())

		for i in range(len(self.illegal_moves)):
			with self.subTest(i=i):
				m = list(self.illegal_moves[i])
				new_val = m.pop()
				old_val = self.p.get(m[0], m[1])
				self.p.grid[m[0]][m[1]] = new_val
				self.assertFalse(self.p.is_puzzle_valid())
				self.p.grid[m[0]][m[1]] = old_val
				self.assertTrue(self.p.is_puzzle_valid())

	def test_is_solved(self):
		"""
		Correctly tell us if a puzzle is solved
		"""
		self.assertFalse(self.p.is_solved())

		v = self.s.get(0, 0)
		self.s.clear(0, 0)
		self.assertFalse(self.s.is_solved())

		self.s.set(0, 0, v)
		self.assertTrue(self.s.is_solved())

	def test_play_legal_game(self):
		"""
		Plays an entire game consisting of only legal moves.
		"""
		self.assertFalse(self.p.is_solved()) # test data error
		self.assertTrue(self.s.is_solved())

		for m in self.p.get_all_empty_cells():
			self.p.set(m[0], m[1], self.s.get(m[0], m[1]))
		self.assertTrue(self.p.is_solved())

	def test_play_dodgy_game(self):
		"""
		Plays an entire game, including some illegal moves.
		"""
		self.assertFalse(self.p.is_solved()) # test data error

		# Make some legal moves
		for m in self.legal_moves:
			self.subTest(f"Legal move: {m}")
			self.p.set(m[0], m[1], m[2])
		self.assertTrue(self.p.is_puzzle_valid())

		# Attempt to make some illegal moves
		for m in self.illegal_moves:
			self.subTest(f"Illegal move {m}")
			self.assertTrue(len(m) == 3)
			self.assertFalse(self.p.is_legal_value(m[0], m[1], m[2]))
			self.assertRaises(ValueError, self.p.set, m[0], m[1], m[2])
		self.assertTrue(self.p.is_puzzle_valid())

		# Finish the game
		for m in self.p.get_all_empty_cells():
			v = self.s.get(m[0], m[1])
			if not self.p.is_legal_value(m[0], m[1], v+1):
				self.assertRaises(ValueError, self.p.set, m[0], m[1], v+1)
			self.p.set(m[0], m[1], v)

		self.assertTrue(self.p.is_solved())

	def test_all_sample_puzzles(self):
		"""
		Loads all the sample puzzles to check for formattign and validity.
		"""
		for puz in sudoku.SAMPLE_PUZZLES:
			with self.subTest(puz['label']):
				p = sudoku.SudokuPuzzle(puz['puzzle'])
				self.assertTrue(p.is_puzzle_valid())

	def test_as_string(self):
		"""
		Just tests that we get *some* kind of string. Also tests as_html
		"""
		self.assertTrue(len(self.p.__str__()) > 160)
		self.assertTrue(len(self.p.as_html()) > 900)

class TestSudokuConstrained(unittest.TestCase):
	def setUp(self):
		self.p = sudoku.SudokuPuzzleConstrained(TEST_PUZZLE)
		self.s = sudoku.SudokuPuzzle(SOLVED_PUZZLE)
		self.legal_moves = LEGAL_MOVES
		self.illegal_moves = ILLEGAL_MOVES

	def test_class_init(self):
		"""
		Test that class init...works
		"""
		p = sudoku.SudokuPuzzleConstrained()
		self.assertFalse(p.is_solved())

	def test_clear_and_set(self):
		"""
		Correctly clear and set a value
		"""
		x = 1
		y = 1
		test_value = TEST_PUZZLE[x][y]
		self.assertNotEqual(test_value, sudoku.EMPTY_CELL) # test data error

		self.p.clear(x, y)
		self.assertTrue(self.p.is_empty(x, y))
		self.p.set(x, y, test_value)
		self.assertEqual(self.p.get(x, y), test_value)
		self.assertFalse(self.p.is_empty(x, y))

	def test_allowed_values(self):
		with self.subTest(f"allowed_values_for_row"):
			self.assertEqual(self.p.allowed_values_for_row[0], {1, 2, 3, 7})
			self.assertEqual(self.p.allowed_values_for_row[1], {2, 6, 7, 8})
			self.assertEqual(self.p.allowed_values_for_row[6], {1, 2, 3, 4, 5, 6, 7, 9})
			self.assertEqual(self.p.allowed_values_for_row[8], {5, 7, 8, 9})

		with self.subTest(f"allowed_values_for_col"):
			self.assertEqual(self.p.allowed_values_for_col[0], {2, 3, 5, 6, 7})
			self.assertEqual(self.p.allowed_values_for_col[6], {1, 3, 4, 5, 6, 7, 9})
			self.assertEqual(self.p.allowed_values_for_col[8], {1, 2, 4, 7, 9})

		with self.subTest(f"allowed_values_for_cage"):
			self.assertEqual(self.p.allowed_values_for_cage[0], {2, 3, 5, 6, 7})
			self.assertEqual(self.p.allowed_values_for_cage[2], {1, 2, 3, 4, 7})
			self.assertEqual(self.p.allowed_values_for_cage[8], {2, 4, 5, 6, 9})

		with self.subTest(f"allowed_values updated (6,6) <- 6"):
			self.p.set(6, 6, 6)
			self.assertEqual(self.p.allowed_values_for_row[6], {1, 2, 3, 4, 5, 7, 9})
			self.assertEqual(self.p.allowed_values_for_col[6], {1, 3, 4, 5, 7, 9})
			self.assertEqual(self.p.allowed_values_for_cage[8], {2, 4, 5, 9})


	def test_possible_values(self):
		"""
		Test that function returns legal values 
		"""
		with self.subTest("Checking possible values"):
			self.assertEqual(self.p.get_possible_values(0, 0), {8})
			self.assertEqual(self.p.get_possible_values(2, 2), {2, 3, 5, 6, 7})
			self.assertEqual(self.p.get_possible_values(7, 0), {5, 6})
			self.assertEqual(self.p.get_possible_values(4, 4), {6})

		with self.subTest("Possible values are legal"):
			for x in range(sudoku.MAX_CELL_VALUE):
				for y in range(sudoku.MAX_CELL_VALUE):
					vlist = self.p.get_possible_values(x,y)
					with self.subTest(f"Cell {x},{y} <- {vlist}"):
						if self.p.is_empty(x, y):
							self.assertTrue(len(vlist) >= 1)
						else:
							self.assertTrue(len(vlist) == 1)

						# Unlike the equivalent test in SudokuPuzzle, we don't assertTrue(is_legal_value) for every value in vlist,
						# because it will return False for some values in v when that value is the only option for some other
						# cell in that row, column, or cage. Which is correct behaviour for is_legal_value and entirely the point.
						# Best we can do here is check that the correct answer is always in the possible list.
						self.assertTrue(SOLVED_PUZZLE[x][y] in vlist)
		return

	def test_legal_move(self):
		"""
		Correctly tell us if a move is legal
		"""
		for m in self.legal_moves:
			with self.subTest(f"Legal move {m} is_legal_value"):
				# Expect this to be "legal"
				self.assertTrue(self.p.is_legal_value(m[0], m[1], m[2]))

		for m in self.legal_moves:
			with self.subTest(f"Legal move {m} is among allowed values"):
				if self.p.is_empty(m[0], m[1]):
					self.assertTrue(m[2] in self.p.allowed_values_for_row[m[0]])
					self.assertTrue(m[2] in self.p.allowed_values_for_col[m[1]])
					self.assertTrue(m[2] in self.p.allowed_values_for_cage[sudoku.cagexy_to_num(m[0], m[1])])
				self.assertTrue(m[2] in self.p.get_possible_values(m[0], m[1]))

		for m in self.legal_moves:
			with self.subTest(f"Legal move {m} can set cell and updates allowed values"):
				# After writing value in cell, expect it to be only possible value for that cell
				self.p.set(m[0], m[1], m[2])
				self.assertEqual(self.p.get_possible_values(m[0], m[1]), set([m[2]]))

				# Expect the value to no longer be allowed in that row, column, or cage
				self.assertTrue(m[2] not in self.p.allowed_values_for_row[m[0]])
				self.assertTrue(m[2] not in self.p.allowed_values_for_col[m[1]])
				self.assertTrue(m[2] not in self.p.allowed_values_for_cage[sudoku.cagexy_to_num(m[0], m[1])])

	def test_play_legal_game(self):
		"""
		Plays an entire game consisting of only legal moves.
		"""
		self.assertFalse(self.p.is_solved()) # test data error
		self.assertTrue(self.s.is_solved()) # test data error

		for m in self.p.get_all_empty_cells():
			self.p.set(m[0], m[1], self.s.get(m[0], m[1]))
		self.assertTrue(self.p.is_solved())

	def test_play_dodgy_game(self):
		"""
		Plays an entire game, including some illegal moves.
		"""
		self.assertFalse(self.p.is_solved()) # test data error

		# Make some legal moves
		with self.subTest("Legal moves"):
			for m in self.legal_moves:
				with self.subTest(f"Legal move: {m}"):
					self.p.set(m[0], m[1], m[2])
			self.assertTrue(self.p.is_puzzle_valid())

		# Attempt to make some illegal moves
		with self.subTest("Illegal moves"):
			for m in self.illegal_moves:
				with self.subTest(f"Illegal move: {m}"):
					self.assertFalse(self.p.is_legal_value(m[0], m[1], m[2]))
					self.assertRaises(ValueError, self.p.set, m[0], m[1], m[2])
			self.assertTrue(self.p.is_puzzle_valid())

		# Finish the game
		with self.subTest("Finish game"):
			for m in self.p.get_all_empty_cells():
				v = self.s.get(m[0], m[1])
				with self.subTest(f"{m}={v}"):
					if not self.p.is_legal_value(m[0], m[1], v+1):
						self.assertRaises(ValueError, self.p.set, m[0], m[1], v+1)
					self.p.set(m[0], m[1], v)

			self.assertTrue(self.p.is_solved())
		return

if __name__ == '__main__':
	unittest.main()
