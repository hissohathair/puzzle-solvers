# benchmarking.py

import copy
import timeit
import sudoku
from sudoku import EMPTY_CELL, CAGE_SIZE, MAX_CELL_VALUE

class BenchmarkerPuzzle(sudoku.SudokuPuzzleConstrained):
	def foo(self):
		return

def bench(function, use_class=sudoku.SudokuPuzzleConstrained, setup=''):
	p = use_class(sudoku.SAMPLE_PUZZLES[6]['puzzle'])
	t = timeit.timeit(f"{function}", globals = {'p': p}, setup=setup)
	print(f"{use_class.__name__} - {function} \t= {t}")
	return

# Sanity check
p = BenchmarkerPuzzle(sudoku.SAMPLE_PUZZLES[6]['puzzle'])
assert([m for m in p.next_empty_cell()] == p.get_all_empty_cells())

print("GET EMPTY CELLS")
bench('p.find_empty_cell()', use_class=BenchmarkerPuzzle)
bench('next(gen)', setup='gen = p.next_empty_cell(loop_once=False)')
bench('p.find_empty_cell()')
