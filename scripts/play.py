# play

import sudoku as su
import cProfile


def play_sudoku(p, s, puzzle):
    assert(not p.is_solved())
    print(p)
    s.solve(p)
    print(p)
    return


puzzle = '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..'
# cProfile.run("play_sudoku_1(puzzle)", sort="tottime")

p = su.SudokuPuzzle()
s = su.SudokuSolver(method='constraintpropogation')
for i in range(4):
    p.init_puzzle(starting_grid=puzzle)
    # cProfile.run("play_sudoku(p, puzzle)", sort="tottime")
    play_sudoku(p, s, puzzle)
