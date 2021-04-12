# Sudoku

Notebooks to finish / polish:

* ~~[Introduction / Index](Sudoku.ipynb)~~
* ~~[Cheating](Sudoku/Cheating.ipynb)~~
* ~~[Constraint Propogation Variability](Constraint%20Propogation%20Variability.ipynb)~~
* [Larger Puzzles](Larger%20Puzzles.ipynb)
* [Performance](Performance.ipynb)
* Maybe: "Unsolveable" or "multiple solutions" tolerance


## tester.py

* `run_single_test` stashes last puzzle test result as private instance variable - feels dodgy. I don't like it.


## sudoku.py

* Why is `StopIteration` never raised line 230?
* Solver should take a timelimit parameter (or PuzzleTester should be able to timeout a solver)
* Solver (all classes really) needs a `__repr__` method


## Sudoku Solver.ipynb

* Add tests / data for unsolvable and multi-solvable puzzles? (https://www.sudokudragon.com/unsolvable.htm)


## Reading

* Benchmarking: https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/ and https://codingnest.com/modern-sat-solvers-fast-neat-and-underused-part-1-5-of-n/
* Read: https://gist.github.com/nickponline/9c91fe65fef5b58ae1b0
* Read: Kaggle 1M Sudoku puzzles https://www.kaggle.com/bryanpark/sudoku
* Read: Modern SAT solvers: https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/
* MIP (Mixed Integer Programming)
** Python library: http://www.pyomo.org/
** Formulating problems: https://people.eecs.berkeley.edu/~vazirani/algorithms/chap7.pdf
** Recommended to learn Linear Programming first
