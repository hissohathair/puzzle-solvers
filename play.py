# play

import sudoku as su
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


def play_sudoku(p, s, puzzle):
    assert(not s.is_solved())
    s.solve()
    assert(s.is_solved())
    print(f"{s}\n")
    assert s.is_solved()


puzzle = '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..'
# cProfile.run("play_sudoku_1(puzzle)", sort="tottime")

p = su.SudokuPuzzle()
p.init_puzzle(puzzle)
s = su.SudokuSolver(p, method='constraintpropogation')
for i in range(4):
    # cProfile.run("play_sudoku(p, puzzle)", sort="tottime")
    play_sudoku(p, s, puzzle)
    s.reset()
