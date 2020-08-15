# play

import sudoku
import cProfile


def solve_using_backtracking(puzzle):
    """
    Attempts to solve `puzzle` using backtracking, trying legal values and
    testing first. Returns True if puzzle is solved, False if the current
    solution path is a dead-end (results in invalid puzzle).
    """
    if puzzle.num_empty_cells() <= 0:
        return True

    mtGen = puzzle.next_best_empty_cell()
    try:
        empty_cell = next(mtGen)
    except StopIteration:
        return True

    x, y = empty_cell[0], empty_cell[1]
    for val in puzzle.get_allowed_values(x, y):
        puzzle.set(x, y, val)
        if solve_using_backtracking(puzzle):
            return True
        else:
            puzzle.clear(x, y)

    return False


def play_sudoku(i=0, use_class=sudoku.SudokuPuzzle):
    p = use_class()
    p.init_puzzle('4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......')
    print(p)

    solve_using_backtracking(p)
    print("\nSolution:")
    print(p)
    assert p.is_solved()


cProfile.run("play_sudoku(5)", sort="tottime")
