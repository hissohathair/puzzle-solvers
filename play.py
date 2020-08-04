# play

import sudoku
import copy
import cProfile

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

def solve_using_backtracking(puzzle):
    """
    Attempts to solve `puzzle` using backtracking, trying legal values and testing first. Returns True if puzzle is solved, 
    False if the current solution path is a dead-end (results in invalid puzzle). Calls itself recursively.
    """
    empty_cell = puzzle.get_first_empty_cell()
    if len(empty_cell) == 0:
        return True
    
    x, y = empty_cell[0], empty_cell[1]
    for val in puzzle.get_possible_values(x,y):
        #if not puzzle.is_legal(x, y, val):
        #    continue
        try:
        	puzzle.set(x, y, val)
        except ValueError:
        	continue

        n = puzzle.update_using_constraints()
        print(f"Updated {n} additional cells based on constraints")
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

cProfile.run('play_sudoku(6)', sort='tottime')