"""Some simple functions for showing puzzles in Jupyter notebooks.

Module variables:
    SUDOKU_CSS: String to use in display(HTML(..)) to format HTML tables
        as a Sudoku grid.
"""

from IPython.display import HTML, display, clear_output


def print_puzzle(puzzle, **args):
    display(HTML(puzzle.as_html(**args)))


def print_2_puzzles(puz1, puz2, **args):
    ret = ['<table><tr><td>', puz1.as_html(**args), '</td>',
           '<td>', puz2.as_html(**args), '</td></tr></table>',
           ]
    display(HTML(''.join(ret)))


def update_progress(label, current, total, time_so_far, test_case):
    clear_output(wait=True)
    display(HTML(f'<progress style="width: 100%" max={total} value={current}>{current} of {total}</progress>'))
    if test_case:
        display(HTML(f"<p>Working on {label}: <i>{test_case}</i> ({current} of {total}), time so far {time_so_far:.2f}s</p>"))
    else:
        display(HTML(f"<p>Completed {total} test cases in {time_so_far:.2f} seconds</p>"))


SUDOKU_CSS = '''
    <style type="text/css">
    .sudoku table {
        border: 3px solid red;
        text-align: center;
        vertical-align: middle;
    }

    .sudoku td {
        width: 40px;
        height: 40px;
        border: 1px solid #F00;
    }

    .sudoku td:nth-of-type(3n) {
        border-right: 3px solid red;
    }

    .sudoku tr:nth-of-type(3n) td {
        border-bottom: 3px solid red;
    }

    .sudoku.solved table {
        border: 3px solid green;
    }

    .sudoku.solved td {
        border: 1px solid green;
    }

    .sudoku.solved td:nth-of-type(3n) {
        border-right: 3px solid green;
    }

    .sudoku.solved tr:nth-of-type(3n) td {
        border-bottom: 3px solid green;
    }

    </style>
'''
