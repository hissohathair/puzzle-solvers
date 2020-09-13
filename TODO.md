# puzzlegrid.py

* `int2char` (line 41) doesn't appear to be used?
* Reture init_puzzle_from_grid -- not needed
* `ConstraintPuzzle` constructor never takes a `starting_grid`?
* Why does `find_empty_cells` never return empty set (line 245)?
* `get_all_empty_cells` (line 276) never used
* Sometimes `x; i; or row` used for rows; sometimes `y; j; or col` uses for columns -- should be consistent
* `as_grid` (line 356) never used
* `__str__` (line 362) never used,  but should probably be `__repr__` anyway
* `drop_testcases` (line 456) never used and has inconsistent naming (should be `drop_test_cases`)
* `run_single_test` stashes last puzzle test result as private instance variable - feels dodgy?

# sudoku.py
* `set` probably doesn't need to check if cell already set because super does that already (line 67)
* Why is `StopIteration` never raised line 230?

# Sudoku Solver.ipynb
* Function `print_puzzle` never used?
* Consider boxplot: https://matplotlib.org/3.1.1/gallery/statistics/boxplot_color.html#sphx-glr-gallery-statistics-boxplot-color-py
* Credit fix: SAT solver actually from here: https://github.com/ContinuumIO/pycosat/blob/master/examples/sudoku.py found via http://ilan.schnell-web.net/prog/sudoku/

# data/
* Multi-solution puzzles?
** 060000092002100080007400000003026000000030604070000500200000050000005000400081000
** 400300600000000701000000008009050000000070050016800003005900000020500000040010026
** 690200040100500008300000000000730005900008000008000200000004000000009500041002007
* Unsolvable examples (because mistake made: https://www.sudokudragon.com/unsolvable.htm)
** 5168497323.76.5...8.97...65135.6.9.7472591..696837..5.253186.746842.75..791.5.6.8
** 781543926..61795..9546287316958372141482653793279148..413752698..2...4..5794861.3
* Two solutions
** .8...9743.5...8.1..1.......8....5......8.4......3....6.......7..3.5...8.9724...5.
** 9.6.7.4.3...4..2...7..23.1.5.....1...4.2.8.6...3.....5.3.7...5...7..5...4.5.1.7.8
* Really hard: https://theconversation.com/good-at-sudoku-heres-some-youll-never-complete-5234
** ....74316...6.384......85..7258...34....3..5......2798..894.....4..859..971326485
** ...7.....1...........43.2..........6...5.9.........418....81.....2....5..4....3..


# Reading
* Benchmarking: https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/ and https://codingnest.com/modern-sat-solvers-fast-neat-and-underused-part-1-5-of-n/
* Read: https://gist.github.com/nickponline/9c91fe65fef5b58ae1b0
* Read: Kaggle 1M Sudoku puzzles https://www.kaggle.com/bryanpark/sudoku
* Read: Modern SAT solvers: https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/
* MIP (Mixed Integer Programming)
** Python library: http://www.pyomo.org/
** Formulating problems: https://people.eecs.berkeley.edu/~vazirani/algorithms/chap7.pdf
** Recommended to learn Linear Programming first
