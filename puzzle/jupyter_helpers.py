"""Some simple functions for showing puzzles in Jupyter notebooks.

Module variables:
    SUDOKU_CSS: String to use in display(HTML(..)) to format HTML tables
        as a Sudoku grid.
"""


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
