# play

import sudoku
import copy
import cProfile

def solve_using_backtracking(puzzle):
    """
    Attempts to solve `puzzle` using backtracking, trying legal values and testing first. Returns True if puzzle is solved, 
    False if the current solution path is a dead-end (results in invalid puzzle). Calls itself recursively.
    """
    if puzzle.num_empty_cells() <= 0:
    	return True

    mtGen = puzzle.next_empty_cell()
    try:
    	empty_cell = next(mtGen)
    except StopIteration:
    	return True

    x, y = empty_cell[0], empty_cell[1]
    for val in puzzle.get_possible_values(x,y):
        puzzle.set(x, y, val)
        if solve_using_backtracking(puzzle):
            return True
        else:
            puzzle.clear(x, y)

    return False

def play_sudoku(i=0, use_class=sudoku.SudokuPuzzleConstrained):
	p = use_class(sudoku.SAMPLE_PUZZLES[i]['puzzle'])
	print(sudoku.SAMPLE_PUZZLES[i]['label'])
	print(p)

	solve_using_backtracking(p)
	print("\nSolution:")
	print(p)
	assert(p.is_solved())
	return

cProfile.run('play_sudoku(5)', sort='tottime')