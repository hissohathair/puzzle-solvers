# benchmarking.py

import timeit
import sudoku
from sudoku import EMPTY_CELL, CAGE_SIZE, MAX_CELL_VALUE

class BenchmarkerPuzzle(sudoku.SudokuPuzzleConstrained):
	def get_row_values_set(self, x, include_empty=True):
		"""
		Return the list of values from row x as a list
		"""
		if include_empty:
			return set(self.grid[x])
		else:
			ret = set(self.grid[x])
			ret.remove(sudoku.EMPTY_CELL)
			return ret

	def get_column_values_set(self, y, include_empty=True):
		"""
		Return the list of values from column y as a list
		"""
		if include_empty:
			return set([i[y] for i in self.grid])
		else:
			ret = set([i[y] for i in self.grid])
			ret.remove(sudoku.EMPTY_CELL)
			return ret

	def get_cage_values_set(self, x, y, include_empty=True):
		"""
		Return the list of values from the cage containing cell x,y as a list
		"""
		cage_x = (x // sudoku.CAGE_SIZE) * sudoku.CAGE_SIZE
		cage_y = (y // sudoku.CAGE_SIZE) * sudoku.CAGE_SIZE
		values = set([i[cage_x:cage_x+sudoku.CAGE_SIZE] for i in self.grid[cage_x:cage_y]])

		if not include_empty and sudoku.EMPTY_CELL in values:
			values.remove(sudoku.EMPTY_CELL)
		return values

	def get_row_values_1(self, x, include_empty=True):
		"""
		Return the list of values from row x as a list
		"""
		if include_empty:
			return list(self.grid[x])
		else:
			return list(filter(lambda a: a != EMPTY_CELL, self.grid[x]))

	def get_column_values_1(self, y, include_empty=True):
		"""
		Return the list of values from column y as a list
		"""
		values = []
		for x in range(MAX_CELL_VALUE):
			if include_empty:
				values.append(self.grid[x][y])
			elif self.grid[x][y] != EMPTY_CELL:
				values.append(self.grid[x][y])
		return values

	def get_cage_values_1(self, x, y, include_empty=True):
		"""
		Return the list of values from the cage containing cell x,y as a list
		"""
		values = []
		cage_x = (x // CAGE_SIZE) * CAGE_SIZE
		cage_y = (y // CAGE_SIZE) * CAGE_SIZE
		for i in range(cage_x, cage_x + CAGE_SIZE):
			for j in range(cage_y, cage_y + CAGE_SIZE):
				if include_empty:
					values.append(self.grid[i][j])
				elif self.grid[i][j] != EMPTY_CELL:
					values.append(self.grid[i][j])
		return values


def bench(function):
	p = BenchmarkerPuzzle(sudoku.SAMPLE_PUZZLES[6]['puzzle'])
	t = timeit.timeit(f"x = p.{function}", globals = {'p': p})
	print(f"{function} \t= {t}")
	return

print("SET")
bench('set(0, 0, 4)')
bench('set_new(0, 0, 4)')

print("\nGET ROWS")
bench('get_row_values(6, True)')
bench('get_row_values(6, False)')

bench('get_row_values_1(6, True)')
bench('get_row_values_1(6, False)')

bench('get_row_values_set(6, True)')
bench('get_row_values_set(6, False)')


print("\nGET COLS")
bench('get_column_values(6, True)')
bench('get_column_values(6, False)')

bench('get_column_values_1(6, True)')
bench('get_column_values_1(6, False)')

bench('get_column_values_set(6, True)')
bench('get_column_values_set(6, False)')

print("\nGET CAGE")
bench('get_cage_values(6, 6, True)')
bench('get_cage_values(6, 6, False)')

bench('get_cage_values_1(6, 6, True)')
bench('get_cage_values_1(6, 6, False)')

bench('get_cage_values_set(6, 6, True)')
bench('get_cage_values_set(6, 6, False)')
