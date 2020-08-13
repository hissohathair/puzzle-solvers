# benchmarking.py

import timeit
import sudoku


class BenchmarkerPuzzle(sudoku.SudokuPuzzle):
    def foo(self):
        return


def bench(function, use_class=sudoku.SudokuPuzzle, setup=""):
    p = use_class()
    p.init_puzzle(sudoku.SAMPLE_PUZZLES[6]["puzzle"])
    t = timeit.timeit(f"{function}", globals={"p": p}, setup=setup)
    print(f"{use_class.__name__} - {function} \t= {t}")
    return


# Sanity check
p = BenchmarkerPuzzle()
assert [m for m in p.next_empty_cell()] == p.get_all_empty_cells()

print("GET EMPTY CELLS")
bench("p.find_empty_cell()", use_class=BenchmarkerPuzzle)
bench("p.get_all_empty_cells()")
