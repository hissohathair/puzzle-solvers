#!/usr/bin/env python

import fileinput

# ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPH = '123456789ABCDEFGHIJKLMNOPQ'
HEXA = '123456789ABCDEFGHIJKLMNOPQ'

in_headrow = True
puzzle1 = []
puzzle2 = []
linenum = 0
for line in fileinput.input():
    linenum += 1
    if in_headrow:
        in_headrow = False
        continue

    line = line.rstrip()
    line = line.replace('0', '.')
    bits = [HEXA[ALPH.index(x)] if x else '.' for x in line.split(',')]
    puzzle1.append(''.join(bits[0:15]))
    puzzle1.append(''.join(bits[16:31]))

    if len(puzzle1) == 16:
        in_headrow = True
        print(''.join(puzzle1))
        print(''.join(puzzle2))
        puzzle1 = []
        puzzle2 = []
