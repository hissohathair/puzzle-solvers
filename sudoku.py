# sudoku class
#
# Class to manage a Sudoku Puzzle. Builds in ConstraintPuzzle
# from puzzlegrid package.
#

import puzzlegrid as pg

DEFAULT_BOX_SIZE = 3


class SudokuPuzzle(pg.ConstraintPuzzle):
    def __init__(self, box_size=DEFAULT_BOX_SIZE):
        """
        Creates a Sudoku puzzle grid. The size to pass is the `box_size` which is 3 for the
        standard 9x9 puzzle, because the "boxes" are 3x3.
        """
        grid_size = box_size * box_size
        super().__init__(grid_size=grid_size)
        self._box_size = box_size

        # Sudoku puzzles have an extra constraint -- boxes cannot contain repeated values
        self._allowed_values_for_box = [
            set(self._complete_set) for i in range(grid_size)
        ]
        return

    def box_num_to_xy(self, i):
        """
        Take the "boxes" to be numbered from 0 to 8, starting with 0 in the top left,
        then running left to right and down the rows so that 8 is bottom right:
        0 (0,0)   1 (0, 3)   2 (0, 6)
        3 (3,0)   4 (3, 3)   5 (3, 6)
        6 (6,0)   7 (6, 3)   8 (6, 6)
        """
        x = (i // 3) * self._box_size
        y = (i % 3) * self._box_size
        return (x, y)

    def box_xy_to_num(self, x, y):
        """
        Given a call at x,y return what the sequential box number is.
        """
        box_x = x // self._box_size
        box_y = y // self._box_size
        return (box_x * self._box_size) + box_y

    def set(self, x, y, v):
        """
        Calls the parent (ConstraintPuzzle) set method first, then updates our additional
        box constraint.
        """
        if self._grid[x][y] == v:
            return
        super().set(x, y, v)

        # Update box constraints
        self._allowed_values_for_box[self.box_xy_to_num(x, y)].remove(v)
        return

    def clear(self, x, y):
        """
        Clears the value at x,y. Will update the box constraints.
        """
        if not self._grid[x][y]:
            return

        # Stash previous value, then clear cell
        prev = self._grid[x][y]
        super().clear(x, y)

        # This value available again for this box
        self._allowed_values_for_box[self.box_xy_to_num(x, y)].add(prev)
        return

    def get_box_values(self, x, y):
        """
        Return the list of values from the box containing cell x,y as a list.
        """
        box_x = (x // self._box_size) * self._box_size
        box_y = (y // self._box_size) * self._box_size
        values = [
            i[box_y:box_y + self._box_size]
            for i in self._grid[box_x:box_x + self._box_size]
        ]
        return [i for sublist in values for i in sublist if i]

    def get_allowed_values(self, x, y):
        """
        Returns the current set of possible values at x, y. This is based on the intersection
        of the sets of allowed values for the same row, column and box. If there is a value
        in the cell, then it is the only allowed value.
        """
        if self._grid[x][y]:
            return set([self._grid[x][y]])
        else:
            return super().get_allowed_values(x, y) & self._allowed_values_for_box[self.box_xy_to_num(x, y)]

    def is_puzzle_valid(self):
        """
        Returns True if the puzzle is still valid (i.e. obeys the rules). Empty cells are allowed.
        We only need to check the box constraint (parent class does rows and columns already).
        This method should *always* return True, since it should not be possible to put a puzzle
        into an invalid state (not without accessing self._grid directly...)
        """
        # Does any box contain repeated values?
        for i in range(self._max_cell_value):
            pos = self.box_num_to_xy(i)
            values = self.get_box_values(pos[0], pos[1])
            if len(values) != len(set(values)):
                return False

        return super().is_puzzle_valid()

    def as_html(self, show_possibilities=0):
        """
        Renders the current puzzle in simple HTML. If show_possibilities > 0, then cells
        with fewer possible values than that will show the possible values.
        """
        data = []
        for x in range(self._max_cell_value):
            row_to_show = []
            for y in range(self._max_cell_value):
                if not self.is_empty(x, y):
                    row_to_show.append(self.get(x, y))
                elif len(self.get_allowed_values(x, y)) < show_possibilities:
                    row_to_show.append(self.get_allowed_values(x, y))
                else:
                    row_to_show.append(" ")
            data.append(row_to_show)

        css_class = "sudoku"
        if self.is_solved():
            css_class += " sudoku-solved"

        ret = '<table class="{}"><tr>{}</tr></table>'.format(
            css_class,
            "</tr><tr>".join(
                "<td>{}</td>".format("</td><td>".join(str(_) for _ in row))
                for row in data
            ),
        )
        return ret


# Some puzzles for testing
SAMPLE_PUZZLES = [
    {
        "level": "Kids",
        "label": "SMH 1",
        "puzzle": [
            [8, 9, 0, 4, 0, 0, 0, 5, 6],
            [1, 4, 0, 3, 5, 0, 0, 9, 0],
            [0, 0, 0, 0, 0, 0, 8, 0, 0],
            [9, 0, 0, 0, 0, 0, 2, 0, 0],
            [0, 8, 0, 9, 6, 5, 0, 4, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 5],
            [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 2, 1, 0, 7, 8],
            [4, 2, 0, 0, 0, 6, 0, 1, 3],
        ],
    },
    {
        "level": "Easy",
        "label": "SMH 2",
        "puzzle": [
            [7, 4, 3, 8, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 9, 6, 0, 0, 0],
            [0, 5, 0, 0, 8, 0, 0, 6, 0],
            [8, 0, 4, 7, 0, 9, 3, 0, 0],
            [0, 0, 0, 0, 0, 5, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 0, 9],
            [9, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 6, 0, 0, 0, 0, 7, 8, 2],
        ],
    },
    {
        "level": "Easy",
        "label": "KTH 1",
        "link": "https://www.diva-portal.org/smash/get/diva2:721641/FULLTEXT01.pdf",
        "puzzle": [
            [0, 0, 0, 0, 3, 7, 0, 9, 2],
            [6, 3, 0, 0, 0, 0, 0, 0, 0],
            [0, 9, 0, 0, 0, 2, 3, 0, 5],
            [8, 7, 0, 0, 0, 0, 0, 0, 1],
            [0, 2, 0, 9, 0, 1, 0, 4, 0],
            [9, 0, 0, 0, 0, 0, 0, 2, 7],
            [1, 0, 9, 5, 0, 0, 0, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 8, 6],
            [3, 6, 0, 4, 1, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Easy",
        "label": "Rico Alan Heart",
        "link": "https://www.flickr.com/photos/npcomplete/2304241247/in/photostream/",
        "puzzle": [
            [0, 2, 1, 6, 0, 7, 8, 4, 0],
            [7, 0, 0, 0, 1, 0, 0, 0, 3],
            [9, 0, 0, 0, 0, 0, 0, 0, 2],
            [3, 0, 0, 0, 0, 0, 0, 0, 8],
            [2, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 9, 0, 0, 0, 0, 0, 6, 0],
            [0, 0, 4, 0, 0, 0, 7, 0, 0],
            [0, 0, 0, 2, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 8, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Moderate",
        "label": "SMH 3",
        "puzzle": [
            [0, 0, 7, 5, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 9, 8, 0, 0],
            [0, 6, 0, 0, 1, 0, 4, 3, 0],
            [8, 0, 5, 0, 0, 2, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 2, 0, 0],
            [0, 1, 0, 7, 0, 0, 0, 0, 9],
            [0, 0, 3, 0, 0, 8, 0, 0, 4],
            [0, 4, 0, 9, 0, 0, 3, 0, 0],
            [9, 0, 0, 0, 0, 6, 0, 2, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "SMH 4",
        "puzzle": [
            [0, 0, 4, 5, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 9, 8],
            [0, 0, 2, 0, 6, 0, 0, 3, 0],
            [7, 0, 0, 1, 5, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 9, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 5, 6],
            [0, 8, 6, 0, 4, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 1, 7, 0],
            [0, 3, 0, 0, 0, 1, 0, 0, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "SMH 5",
        "puzzle": [
            [0, 0, 8, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 6, 0, 0, 4, 9, 0],
            [5, 0, 0, 0, 0, 0, 0, 7, 0],
            [0, 7, 0, 0, 4, 0, 0, 0, 0],
            [0, 5, 0, 2, 0, 6, 0, 0, 0],
            [8, 0, 0, 7, 9, 0, 0, 1, 0],
            [0, 6, 3, 0, 0, 0, 0, 0, 1],
            [0, 0, 5, 0, 7, 3, 0, 0, 0],
            [0, 0, 0, 9, 0, 0, 7, 5, 0],
        ],
    },
    {
        "level": "Hard",
        "label": "Greg [2017]",
        "link": "https://gpicavet.github.io/jekyll/update/2017/12/16/sudoku-solver.html",
        "puzzle": [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 1",
        "link": "https://www.flickr.com/photos/npcomplete/2384354604",
        "puzzle": [
            [9, 0, 0, 1, 0, 4, 0, 0, 2],
            [0, 8, 0, 0, 6, 0, 0, 7, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 7, 0, 0, 0, 0, 0, 3, 0],
            [3, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 7, 0, 0, 8, 0],
            [1, 0, 0, 2, 0, 9, 0, 0, 4],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 2",
        "link": "https://www.flickr.com/photos/npcomplete/2361922697/in/photostream/",
        "puzzle": [
            [1, 0, 0, 8, 0, 5, 0, 0, 4],
            [0, 2, 0, 0, 6, 0, 0, 9, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 0, 0, 0, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 0, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 5],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 9, 0, 0, 6, 0],
            [5, 0, 0, 4, 0, 7, 0, 0, 8],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan Border #1",
        "link": "https://www.flickr.com/photos/npcomplete/2304241257/in/photostream/",
        "puzzle": [
            [0, 0, 3, 7, 0, 2, 6, 0, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 1],
            [7, 0, 0, 0, 0, 0, 0, 0, 3],
            [0, 4, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 4],
            [9, 0, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 6, 8, 0, 3, 2, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Rico Alan 4",
        "link": "https://www.flickr.com/photos/npcomplete/2361922695/in/photostream/",
        "puzzle": [
            [0, 0, 0, 0, 2, 5, 0, 0, 0],
            [0, 0, 0, 0, 0, 7, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 4, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 5, 9],
            [7, 0, 0, 0, 0, 0, 0, 0, 2],
            [3, 8, 0, 0, 0, 0, 0, 0, 0],
            [0, 9, 5, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 6, 0, 0, 0, 0, 0],
            [0, 0, 0, 8, 3, 0, 0, 0, 0],
        ],
    },
    {
        "level": "Diabolical",
        "label": "Qassim Hamza",
        "link": "https://www.flickr.com/photos/npcomplete/2304537670/in/photostream/",
        "puzzle": [
            [0, 0, 0, 7, 0, 0, 8, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 9, 0, 0, 1],
            [6, 0, 0, 5, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 3, 0, 0, 4, 0],
            [0, 0, 5, 0, 0, 1, 0, 0, 7],
            [5, 0, 0, 2, 0, 0, 6, 0, 0],
            [0, 3, 0, 0, 8, 0, 0, 9, 0],
            [0, 0, 7, 0, 0, 0, 0, 0, 2],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "Rico Alan 3",
        "link": "https://www.flickr.com/photos/npcomplete/2361922699/in/photostream/",
        "puzzle": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 3, 0, 8, 5],
            [0, 0, 1, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 5, 0, 7, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 1, 0, 0],
            [0, 9, 0, 0, 0, 0, 0, 0, 0],
            [5, 0, 0, 0, 0, 0, 0, 7, 3],
            [0, 0, 2, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 9],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "World's Hardest Sudoku 2012",
        "link": "https://www.conceptispuzzles.com/index.aspx?uri=info/article/424",
        "puzzle": [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0],
        ],
    },
    {
        "level": "Pathalogical",
        "label": "AI escargot",
        "link": "http://www.aisudoku.com/index_en.html",
        "puzzle": [
            [1, 0, 0, 0, 0, 7, 0, 9, 0],
            [0, 3, 0, 0, 2, 0, 0, 0, 8],
            [0, 0, 9, 6, 0, 0, 5, 0, 0],
            [0, 0, 5, 3, 0, 0, 9, 0, 0],
            [0, 1, 0, 0, 8, 0, 0, 0, 2],
            [6, 0, 0, 0, 0, 4, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 4, 0, 0, 0, 0, 0, 0, 7],
            [0, 0, 7, 0, 0, 0, 3, 0, 0],
        ],
    },
]
