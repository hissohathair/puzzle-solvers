#!/usr/bin/env python

import fileinput

# ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPH = '123456789ABCDEFGHIJKLMNOPQ'
HEXA = '123456789ABCDEFGHIJKLMNOPQ'

in_headrow = True
puzzle = []
linenum = 0
for line in fileinput.input():
    linenum += 1
    if in_headrow:
        in_headrow = False
        continue

    line = line.rstrip()
    line = line.replace('0', '.')
    # bits = [HEXA[ALPH.index(x)] if x else '.' for x in line]
    puzzle.append(line)

    if len(puzzle) == 9:
        in_headrow = True
        print(''.join(puzzle))
        puzzle = []
