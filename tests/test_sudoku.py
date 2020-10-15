"""Unit tests for puzzle.sudoku classes and functions."""

import os
import unittest

import puzzle.latinsquare as ls
import puzzle.sudoku as su


TEST_PUZZLE_STRINGS = [
    # 4x4
    "21...32....41...",
    "42..1....12....3",
    ".2....2.3.4.2..1",

    # 9x9
    "89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13",
    "..75.....1....98...6..1.43.8.5..2.1.......2...1.7....9..3..8..4.4.9..3..9....6.2.",
    "..8......1..6..49.5......7..7..4.....5.2.6...8..79..1..63.....1..5.73......9..75.",

    # 16x16 - some of these are mostly solved, otherwise they take a long time to test
    "G.1C4.6F92E3A58BAF638G29.B5CED14845EB73..1A6G9F229BDA51EG84F6C73613AG4E857CBD..9BCD732A1FG948E56F28GC95D1E6A4B379E45F67B83D2C1AGCDG12B864F753A9E7A2BE1C43DG9F86538945AFG6C2E17BD56EFD397BA182G4C4B786FDAC53G.2E1EGC29845A6B173D..3A91CB2E4F756G8.5F67EG3298DB4C.",
    "..A8D.B9CF315GE291.DA8..GB2ECF34G...E21C547DA9.62C4EF53G68..1DB7FB..C6...785EAD9....5DF196GB.4788D719A4BE.F3265G36958EG72D4A..C1D52G4B9A3E1..8FCBE6A7.C2FGD..593C937GFD8A564B21E481F635EB29CD7GA74EB396FDACG8125A28C1GED495F736B1GF6B7A583E29C4D53D92C8471B6GE..",
    "1.A7.G68FB59D4CE54..........96FB6GF8ED9BC724A513DCB95F4A13E687G235C...F2E49.6..79E.241D6B8G.3CA5F..4A5G372...8B9B68G.E795D3A2F41C3.5G7B4D61EFA988FD19AE54G73.26CE...28...FB5G...G79BD..F8CA2.E3478GCF4AE35DB19262...19576E4GCD8A..6EBC8D21F743.G415D632GA9C87B..",

    # 25x25
    "H.P.KJ5.6F..O..I2..3B9G7..J..8.DI.25LNGACM9B7.6..O..C..M...A6.HF..85.G.I23D...6..BKP.9.7D3F..J.N.C.MN5.73G9.CLIM......OAFE..84......M....A.F.6G3C.5.DBL6MDGP..OE.I.JB5..K.C....P.....6L...857...DAE3OFG91.BJ5..DF..9.6L.H82MP.I..9....28NH51D..GL4.I..AMEJM.O.6.P5.NGJ..K...F.....EGF.8L.K72MO6I.4N.3.J.......N..C.14....3M.5I92J..L.E..9I.....7PCL.G.4....HAN2PJ..9.AE3..81N6C.DLOG5F7BMK..LN.7H.13AO.G.5D...9..GD.C4M.K..5P..9.ENO.3.I6.86.1.E...BH9KI3..C..J.2F.4FEN.2.J..G.C.BKPMI..OH.7L.OP53...JN...A.2..KD.1G.E.....BG.CO.IHMAF.952J.3.N.1..4PI..7JB8....6.FAMHC7.F.3.O.D..6.2.IK.5......I3..KH.5.L.G...J.4BE.P6CK..G9.CJA6E3DM..PL..7.8..",
    "HA...7.1M.E4.N2..D...93689.....J.N86..H.142PC.GK.B56...LB.EP..1....MIA...C..OI.45.AH27.9M....K6.DLF.M2L8ND6...GCIAF...O...H.EA...J...B.FG8.4P96....I.....K9.15.DM.C.J3.IH7.2.......HO.76J.A...KM...3584.B...CG.H.I.3N.6OJF48MEAP92L.6.4.8.M...P.A..DNBF.O.L.8NA9.J.E1.BFG2CP..HI.D.J45O1.M...LH7DC6EA..G3...I.39D....H..P.N7FK.4OM.B2G..7.I..1K5M.93B.N..C.........6OD.F4.EIAM8.3LN..7.3.......P.ONFB..A5.J17D9IPNC578.M..2I...FOE6.4L.J.D9A..K24I5HP....G3BM...8FF.14..H..9.5.6...C.2KPMA...6EGJAB..3L......1.5O.NH...J..PF..N.3.7G......5.K7HNFL286.B.DM.IC5.......J.3...19O.4B.2...K....NPEDED..I.7N.LCF6.KJ2OA1..G.MKB.15EI...A..8OLD7N..C4..",
    "P9NKJ2B4.1D..C8G..3.M.....CF.3.K...G7L9...1JM...6.B5D..NC.P.J1.M....I.H.A2K.1..A.F.ME..BOK.4...JL....82..I3....NE..P.B7OD1FC.7I.....K.MLD.G51.........K..D.8.....4.3BE2J.HONGA.H.LM86NOJD..2.EK.5AG.4B.34.O..CHA3..FP.16.7...MI5.A.J5..EI.2..N.6CB3M4F.LKD..I..L1.E..J.K.F7.2..HPM63A8.1J..2..M4N..D.H..F5BLF...OB96K..I....J...A2.78....K..F4.83..9...E.NJ..1D.7.....8526.1..PO.I...4E..K....C9..G8..5E.627...I.D.8.H72..A.M.CL....E.6..M2.1.5J...7O9D.AN.8KB.H.P.3AFLG6MN8..5..JOIP.KD2.4..9JG.P.OK.26I.HC4.BL8........P.BA.NLDEI..2...G43.J.5..3I7....G..OL6..PE.DCI.G7P.5.CO..18.B.D.F..KNJ9O6AHKMGD.P.J27.384.5....8.3B.F..LJ4A..ON1.GP6I7HM",
]

TEST_SOLUTION_STRINGS = [
    # 4x4
    "2143432132141432",
    "4231134231242413",
    "4213132431422431",

    # 9x9
    "893472156146358792275619834954183267782965341361247985518734629639521478427896513",
    "387524961124639875569817432835492617796185243412763589673258194248971356951346728",
    "498157632137682495526439178671348529359216847842795316763524981915873264284961753",

    # 16x16
    "G71C4D6F92E3A58BAF638G297B5CED14845EB73CD1A6G9F229BDA51EG84F6C73613AG4E857CBDF29BCD732A1FG948E56F28GC95D1E6A4B379E45F67B83D2C1AGCDG12B864F753A9E7A2BE1C43DG9F86538945AFG6C2E17BD56EFD397BA182G4C4B786FDAC53G92E1EGC29845A6B173DFD3A91CB2E4F756G815F67EG3298DB4CA",
    "67A8D4B9CF315GE2915DA876GB2ECF34GFB3E21C547DA9862C4EF53G68A91DB7FBG4C6231785EAD9EAC25DF196GB34788D719A4BECF3265G36958EG72D4AFBC1D52G4B9A3E1768FCBE6A71C2FGD84593C937GFD8A564B21E481F635EB29CD7GA74EB396FDACG8125A28C1GED495F736B1GF6B7A583E29C4D53D92C8471B6GEAF",
    "12A73G68FB59D4CE54E372C1GA8D96FB6GF8ED9BC724A513DCB95F4A13E687G235CA8BF2E4916GD79E7241D6B8GF3CA5FD14A5G3726CE8B9B68GCE795D3A2F41C325G7B4D61EFA988FD19AE54G73B26CEA46283C9FB5G17DG79BD61F8CA25E3478GCF4AE35DB19262B3F19576E4GCD8AA96EBC8D21F7435G415D632GA9C87BEF",

    # 25x25
    "HDPMKJ546F8COE1I2NL3B9G7AFJE481DI325LNGACM9B7H6KPOO9CLBM7ENA6KHFJ485PG1I23DI2G6A8BKPO947D3FEHJ1NLC5MN5173G9HCLIMB2PKD6OAFE4J84O8NEIJM9KP2AHF76G3CL51DBL6MDGPA3OENI4JB591KFCH782PKI2HB6L14M857CJNDAE3OFG91ABJ57GDFC39E6LOH82MPKIN49C73F28NH51DKOGL4BIP6AMEJM1OC6DP5LNGJ29KH7AF8IB34EGFA8LHK72MO6I54NB3EJ9PDC1DHNB7CO14GAEF3MP5I92J86LKE359I6F8BJ7PCLDGO41K2MHAN2PJK49IAE3HB81N6CMDLOG5F7BMKI2LN67HF13AO8GJ5D4CE9PJGDHC4MFKB25P8791ENOA3LI6A8651OEGDPBH9KI3L7C4MJN2F34FENA29J1DGLC6BKPMI87OH57L9OP53C8IJNM4EAF26HKDB1G6E4PDNLBG8CO1IHMAF7952JK35NL1OE4PI9K7JB823CG6DFAMHC7HFJ31OMD4A6P2EIK85GN9BL8I3AMKH257LFGN9DJO4BE1P6CKB2G9FCJA6E3DM51PLHN748OI",
    "HAJBP7C1MOE4KN25LDFGI936897D3EFJIN86OLH5142PCAGKMB56KGFLB9EPJ813DHNMIA247CO1OIC45GAH27B9MPE38K6JDLFNM2L8ND6K43GCIAF97JOBP1H5EA1OMJ3NEBCFG8L4P9625DKIH748FK9P15ADMECOJ3BIH762NGLNGPIHOF76J9AD2BKMLCE35841B57DCGLH2IK3N16OJF48MEAP92LE634K89MI75PHA1GDNBFJOCLM8NA93J7E1KBFG2CP5OHI6D4J45O1BM28NLH7DC6EA9IG3FKPIE39DA5CLH86PJN7FKG4OM1B2GF276I4P1K5MO93BHNJDC8ELACPBHK6ODGF42EIAM813LNJ9753KH2MCEGP6ONFB84A5LJ17D9IPNC578DM312IAK9FOE6H4LBJGD9ALOK24I5HPJ71NG3BME6C8FFJ14BNHLO9D5G6E8IC72KPMA38I6EGJABF73L4CMDP91K5O2NHOC4J2MPFDAN13E7G6B89LH5IK7HNFL286KBPDMGIC54E39AO1J63GA819OC4BJ25LIKHMF7NPEDED9PIH7N5LCF64KJ2OA18BG3MKBM15EI3JGA9H8OLD7NPFC426",
    "P9NKJ2B461D5FC8GAH3LMOEI7ECFI3OK8HAG7L92D51JM4PN6BB5DO7NCLPGJ13M48FEI6H9A2K61HGA7FDMEIPBOK24NC9JL385L824MI3J59HNE6APKB7OD1FCG7IB3294KFMLDAG518PONC6JEHK61DC8L57PM4I3BE2JFHONGA9HFLM86NOJDC927EKI5AG14BP34GONECHA3BKFPJ1697LD8MI52APJ591EIG2O8NH6CB3M4F7LKDG4I95L1NECBJOKDF7A283HPM63A861JOP27EM4NG9DKHCIF5BLFMCEOB96K35IHLP4JGN1A2D782BPHKDGF4I837A9M6LE5NJCO1DJ7LNMAH8526C1F3POBIGK94ENHKPBADC9LFG84J5EM6273O1IOD48IH72BFAKMPCLG913E56JNM2E165J3I47O9DLANF8KBCHGPC3AFLG6MN81E5BHJOIP7KD294579JGEP1OK326INHC4DBL8MFA1KMCFP8BA6NLDEI7H25J9G43OJN5243I71H9BGFMOL6KAPE8DCILG7P45ECO6H183BMD9F2AKNJ9O6AHKMGDNPCJ27I384E5B1LF8E3BDF29LJ4AK5ON1CGP6I7HM",
]

EASY_PUZZLE = ls.from_string("89.4...5614.35..9.......8..9.....2...8.965.4...1.....5..8.......3..21.7842...6.13")
EASY_SOLUTION = ls.from_string("893472156146358792275619834954183267782965341361247985518734629639521478427896513")
EASY_MOVES_LEGAL = [[0, 2, 3], [3, 3, 1], [4, 4, 6], [1, 6, 7], [7, 3, 5], [1, 8, 2], [8, 2, 7]]
EASY_MOVES_ILLEGAL = [[0, 2, 8], [0, 2, 1], [3, 3, 2], [3, 3, 4], [2, 2, 4], [3, 3, 6], [0, 0, 9]]

HARD_PUZZLE = ls.from_string("..8......1..6..49.5......7..7..4.....5.2.6...8..79..1..63.....1..5.73......9..75.")
HARD_SOLUTION = ls.from_string("498157632137682495526439178671348529359216847842795316763524981915873264284961753")

UNSOLVABLE_STRINGS = [
    "5168497323.76.5...8.97...65135.6.9.7472591..696837..5.253186.746842.75..791.5.6.8",
    "781543926..61795..9546287316958372141482653793279148..413752698..2...4..5794861.3",
]

MULTI_SOLUTION_STRINGS = [
    ".8...9743.5...8.1..1.......8....5......8.4......3....6.......7..3.5...8.9724...5.",
    "9.6.7.4.3...4..2...7..23.1.5.....1...4.2.8.6...3.....5.3.7...5...7..5...4.5.1.7.8",
    ".6.....92..21...8...74.......3.26.......3.6.4.7....5..2......5......5...4...81...",
    "4..3..6........7.1........8..9.5........7..5..168....3..59......2.5......4..1..26",
    "69.2...4.1..5....83...........73...59....8.....8...2.......4........95...41..2..7",
]


class TestSudokuPuzzle(unittest.TestCase):
    def setUp(self):
        self.p = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_PUZZLE)
        self.s = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_SOLUTION)
        self.legal_moves = EASY_MOVES_LEGAL
        self.illegal_moves = EASY_MOVES_ILLEGAL
        return

    def test_class_init_copies(self):
        """Class init makes a copy of starting grid"""
        x = 0
        y = 2
        new_value = 3
        self.assertTrue(self.p.is_empty(x, y))  # test data error
        self.assertNotEqual(self.p.get(x, y), new_value)  # test data error

        # Change value -- puzzle but not original list should change
        self.p.set(x, y, new_value)
        self.assertEqual(new_value, self.p.get(x, y))
        self.assertNotEqual(new_value, EASY_PUZZLE[x][y])
        return

    def test_class_init_empty(self):
        """Class init can create an empty grid"""
        p = su.SudokuPuzzle()
        for x in range(p.max_value):
            for y in range(p.max_value):
                self.assertTrue(p.is_empty(x, y))
        return

    def test_puzzle_sizes(self):
        """Different puzzle sizes are supported"""
        # Initialise all test puzzles, at different sizes
        for i, puz in enumerate(TEST_PUZZLE_STRINGS):
            with self.subTest(f"Test Puzzle {i} init (len={len(puz)})"):
                p = su.SudokuPuzzle(starting_grid=ls.from_string(puz))
                self.assertTrue(p.is_valid())
                self.assertEqual(len(puz), p.num_cells)
        return

    def test_class_init_raises_exception(self):
        """Class init raises an exception for malformed grids"""
        data = [1, 2, 3]
        self.assertRaises(ValueError, self.p.init_puzzle, data)
        data = [[1, 2, 3] for x in range(self.p.max_value)]
        self.assertRaises(ValueError, self.p.init_puzzle, data)
        return

    def test_box_num_toxy(self):
        """Conversion of box numbers to (x,y) positions

        0 (0,0)   1 (0, 3)   2 (0, 6)
        3 (3,0)   4 (3, 3)   5 (3, 6)
        6 (6,0)   7 (6, 3)   8 (6, 6)
        """
        with self.subTest("9x9 grid (3x3 box)"):
            correct_values = [
                (0, 0),
                (0, 3),
                (0, 6),
                (3, 0),
                (3, 3),
                (3, 6),
                (6, 0),
                (6, 3),
                (6, 6),
            ]
            p = su.SudokuPuzzle(grid_size=9)
            for i in range(p.max_value):
                with self.subTest(f"Cage {i} at {correct_values[i]}"):
                    self.assertEqual(correct_values[i], p.box_num_to_xy(i))
                    self.assertEqual(i, p.box_xy_to_num(*correct_values[i]))

        with self.subTest("4x4 grid (2x2 box)"):
            correct_values = [
                (0, 0),
                (0, 2),
                (2, 0),
                (2, 2),
            ]
            p = su.SudokuPuzzle(grid_size=4)
            for i in range(p.max_value):
                with self.subTest(f"Cage {i} at {correct_values[i]}"):
                    self.assertEqual(correct_values[i], p.box_num_to_xy(i))
                    self.assertEqual(i, p.box_xy_to_num(*correct_values[i]))
        return

    def test_box_xy_tonum(self):
        """Conversion of x,y cell positions to box numbers"""
        for x in range(self.p.max_value):
            for y in range(self.p.max_value):
                with self.subTest(f"Cage for {x},{y}"):
                    num = self.p.box_xy_to_num(x, y)
                    pos = self.p.box_num_to_xy(num)
                    self.assertEqual(
                        self.p.box_xy_to_num(x, y), self.p.box_xy_to_num(*pos)
                    )
        return

    def test_clear_and_set(self):
        """Clear and set a value for a cell"""
        x = 1
        y = 1
        test_value = EASY_PUZZLE[x][y]
        self.assertTrue(test_value)  # test data error

        # Clear op
        num_empty = self.p.num_empty_cells()
        self.p.clear(x, y)
        self.assertTrue(self.p.is_empty(x, y))
        self.assertEqual(num_empty + 1, self.p.num_empty_cells())

        # Set op
        self.p.set(x, y, test_value)
        self.assertEqual(self.p.get(x, y), test_value)
        self.assertFalse(self.p.is_empty(x, y))
        self.assertEqual(num_empty, self.p.num_empty_cells())
        return

    def test_get_values(self):
        """Get row, column, and box values"""
        with self.subTest("get_row_values"):
            self.assertEqual(self.p.get_row_values(0), [8, 9, 4, 5, 6])
            self.assertEqual(self.p.get_row_values(7), [3, 2, 1, 7, 8])

        with self.subTest("get_column_values"):
            self.assertEqual(self.p.get_column_values(0), [8, 1, 9, 4])
            self.assertEqual(self.p.get_column_values(7), [5, 9, 4, 7, 1])

        with self.subTest("get_box_values"):
            self.assertEqual(self.p.get_box_values(0), [8, 9, 1, 4])
            self.assertEqual(self.p.get_box_values(6), [8, 3, 4, 2])
            self.assertEqual(self.p.get_box_values(8), [7, 8, 1, 3])
        return

    def test_possible_values(self):
        """Test that function returns legal values"""
        with self.subTest("Checking possible values"):
            self.assertEqual(self.p.get_allowed_values(0, 0), {8})
            self.assertEqual(self.p.get_allowed_values(2, 2), {2, 3, 5, 6, 7})
            self.assertEqual(self.p.get_allowed_values(7, 0), {5, 6})

        with self.subTest("Possible values are legal"):
            for x in range(self.p.max_value):
                for y in range(self.p.max_value):
                    with self.subTest(f"Cell {x},{y}"):
                        vlist = self.p.get_allowed_values(x, y)
                        if self.p.is_empty(x, y):
                            self.assertTrue(len(vlist) >= 1)
                        else:
                            self.assertTrue(len(vlist) == 1)

                        with self.subTest(f"Cell {x},{y} -> {vlist}"):
                            for value in vlist:
                                self.assertTrue(value in self.p.get_allowed_values(x, y))
        return

    def test_legal_move(self):
        """Correctly tell us if a move is legal"""
        for i in range(len(self.legal_moves)):
            with self.subTest(i=i):
                m = self.legal_moves[i]
                self.assertEqual(EASY_SOLUTION[m[0]][m[1]], m[2])  # test data error
                self.assertTrue(m[2] in self.p.get_allowed_values(m[0], m[1]))
        return

    def test_invalid_move(self):
        """Correctly tell us if we use a value out of range for a cell"""
        self.assertRaises(ValueError, self.p.set, 0, 0, 0)
        self.assertRaises(ValueError, self.p.set, 0, 0, self.p.max_value + 1)
        return

    def test_illegal_moves(self):
        """Correctly tell us if a move is NOT legal"""
        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = self.illegal_moves[i]
                self.assertFalse(m[2] in self.p.get_allowed_values(m[0], m[1]))
        return

    def test_illegal_set(self):
        """Throw exception if we attempt an illegal move"""
        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = self.illegal_moves[i]
                self.assertRaises(ValueError, self.p.set, *m)
        return

    def test_is_valid(self):
        """Correctly tell us if a puzzle grid is or is not valid"""
        self.assertTrue(self.p.is_valid())

        for i in range(len(self.illegal_moves)):
            with self.subTest(i=i):
                m = list(self.illegal_moves[i])
                new_val = m.pop()
                old_val = self.p.get(*m)
                self.p._grid[m[0]][m[1]] = new_val
                self.assertFalse(self.p.is_valid())
                self.p._grid[m[0]][m[1]] = old_val
                self.assertTrue(self.p.is_valid())
        return

    def test_is_solved(self):
        """Correctly tell us if a puzzle is solved"""
        self.assertFalse(self.p.is_solved())

        v = self.s.get(0, 0)
        self.s.clear(0, 0)
        self.assertFalse(self.s.is_solved())

        self.s.set(0, 0, v)
        self.assertTrue(self.s.is_solved())
        return

    def test_play_legal_game(self):
        """Plays an entire game consisting of only legal moves"""
        self.assertFalse(self.p.is_solved())  # test data error
        self.assertTrue(self.s.is_solved())

        for m in self.p.next_empty_cell():
            self.p.set(*m, self.s.get(*m))
        self.assertTrue(self.p.is_solved())
        return

    def test_play_all_games(self):
        """Plays multiple games in test data at different puzzle sizes"""
        for i, puz in enumerate(TEST_PUZZLE_STRINGS):
            with self.subTest(f"Puzzle {i} (len={len(puz)})"):
                p = su.SudokuPuzzle(starting_grid=ls.from_string(puz))
                s = su.SudokuPuzzle(starting_grid=ls.from_string(TEST_SOLUTION_STRINGS[i]))
                self.assertFalse(p.is_solved())
                self.assertTrue(s.is_solved())

                for m in p.next_empty_cell():
                    p.set(*m, s.get(*m))
                self.assertTrue(p.is_solved())
        return

    def test_play_dodgy_game(self):
        """Plays an entire game, including some illegal moves"""
        self.assertFalse(self.p.is_solved())  # test data error

        # Make some legal moves
        for m in self.legal_moves:
            self.subTest(f"Legal move: {m}")
            self.p.set(*m)
        self.assertTrue(self.p.is_valid())

        # Attempt to make some illegal moves
        for m in self.illegal_moves:
            self.subTest(f"Illegal move {m}")
            self.assertTrue(len(m) == 3)
            self.assertFalse(m[2] in self.p.get_allowed_values(m[0], m[1]))
            self.assertRaises(ValueError, self.p.set, *m)
        self.assertTrue(self.p.is_valid())

        # Finish the game
        for m in self.p.next_empty_cell():
            v = self.s.get(*m)
            if not (v + 1) in self.p.get_allowed_values(*m):
                self.assertRaises(ValueError, self.p.set, *m, v + 1)
            self.p.set(*m, v)

        self.assertTrue(self.p.is_solved())
        return

    def test_all_sample_puzzles(self):
        """Loads all the sample puzzles to check for formatting and validity"""
        for puz in su.SAMPLE_PUZZLES:
            with self.subTest(puz["label"]):
                self.p.init_puzzle(ls.from_string(puz["puzzle"]))
                self.assertTrue(self.p.is_valid())
        return

    def test_as_string(self):
        """String representations of puzzle grid"""
        self.assertTrue(len(self.p.__str__()) >= 81)
        self.assertTrue(len(self.p.as_html()) > 900)
        self.assertTrue(len(self.p.as_html(show_possibilities=2)) > 950)

        self.assertTrue(len(self.s.__str__()) >= 81)
        self.assertTrue(len(self.s.as_html()) > 900)
        self.assertTrue(len(self.s.as_html(show_possibilities=2)) > 900)
        return


class TestSudokuSolver(unittest.TestCase):
    """Test cases for SudokuSolver"""

    def setUp(self):
        """Handy to have an unsolved (p) and already solved puzzle (s) for later tests"""
        self.p = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_PUZZLE)
        self.s = su.SudokuPuzzle(su.DEFAULT_SUDOKU_SIZE, EASY_SOLUTION)
        return

    def test_backtracking(self):
        """Test the backtracking solution"""
        solver = su.BacktrackingSolver()
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))

        self.p.init_puzzle(HARD_PUZZLE)
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        return

    def test_constraing_propogation(self):
        """Test the backtracking + constraint propogation solution"""
        solver = su.ConstraintPropogationSolver()
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))

        self.p.init_puzzle(HARD_PUZZLE)
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        return

    def test_single_possibilities(self):
        """Solve a puzzle using the 'single possibilities' method (easy only)"""
        solver = su.DeductiveSolver()
        self.assertTrue(solver.solve_single_possibilities(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))
        return

    def test_only_squares(self):
        """Solve a puzzle using 'only squares' method (easy only)"""
        solver = su.DeductiveSolver()

        with self.subTest("Solve some only squares by row"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver._solve_only_row_squares(self.p) > 0)

        with self.subTest("Solve some only squares by column"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver._solve_only_column_squares(self.p) > 0)

        with self.subTest("Solve some only squares by box"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver._solve_only_box_squares(self.p) > 0)

        with self.subTest("Solve using only squares (all)"):
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve_only_squares(self.p))
            self.assertTrue(self.p.is_solved())
            self.assertEqual(str(self.s), str(self.p))
        return

    def test_two_out_of_three(self):
        """Partially solve a puzzle using the "2 out of 3" method"""
        solver = su.DeductiveSolver()
        num_empty = self.p.num_empty_cells()

        # This one can't actually solve the first puzzle, but can solve a
        # few cells
        solver.solve_two_out_of_three(self.p)
        self.assertTrue(self.p.num_empty_cells() < num_empty)
        return

    def test_deductive(self):
        """Solve a puzzle using all deductive methods + back tracking"""
        with self.subTest("DeductiveSolver without backtracking"):
            solver = su.DeductiveSolver(use_backtracking=False)

            # Deductive without backtracking can solve EASY_PUZZLE
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve(self.p))
            self.assertTrue(self.p.is_solved())

            # Deductive without backtracking can NOT solve hard puzzle
            self.p.init_puzzle(HARD_PUZZLE)
            self.assertFalse(solver.solve(self.p))
            self.assertFalse(self.p.is_solved())

        with self.subTest("DeductiveSolver with backtracking"):
            solver = su.DeductiveSolver(use_backtracking=True)

            # Deductive with backtracking can solve hard puzzle
            self.p.init_puzzle(HARD_PUZZLE)
            self.assertTrue(solver.solve(self.p))
            self.assertTrue(self.p.is_solved())
        return

    def test_sat(self):
        """Solve a puzzle with a SAT solver"""
        solver = su.SATSolver()

        # Correct clauses?
        mv = self.p.max_value
        mp = mv - 1
        every_cell_has_a_value = (mv ** 2)
        no_cell_has_two_values = (mp ** 2 + mp) // 2
        num_regions = mv * 3
        regions_have_unique_values = no_cell_has_two_values * mv

        # Assuming test puzzle is 9x9
        assert self.p.num_cells == 81  # test data error
        assert every_cell_has_a_value == 81
        assert no_cell_has_two_values == 36
        assert num_regions == 27
        assert regions_have_unique_values == 324

        expected_clauses = every_cell_has_a_value * (1 + no_cell_has_two_values) + num_regions * regions_have_unique_values
        assert expected_clauses == 11745

        # Every puzzle clue counts for an additional clause
        num_clues = self.p.num_cells - self.p.num_empty_cells()
        expected_clauses += num_clues

        # Check that we generate correct number of clauses
        self.assertEqual(expected_clauses, len(solver.get_sat_clauses(self.p)))

        # Can solve easy & hard puzzles
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        self.assertEqual(str(self.s), str(self.p))

        self.p.init_puzzle(HARD_PUZZLE)
        self.assertTrue(solver.solve(self.p))
        self.assertTrue(self.p.is_solved())
        return

    def test_solver(self):
        """SudokuSolver can be vaguely useful"""
        with self.subTest("Default solver works"):
            solver = su.SudokuSolver()
            self.p.init_puzzle(EASY_PUZZLE)
            self.assertTrue(solver.solve(self.p))

            self.p.init_puzzle(HARD_PUZZLE)
            self.assertTrue(solver.solve(self.p))

        with self.subTest("Bad solver raises exception"):
            self.assertRaises(ValueError, su.SudokuSolver, method="banana")
        return

    def test_all_solvers(self):
        """Test that all available solvers are supported"""
        for x in su.SOLVERS:
            with self.subTest(f"Method {x}"):
                solver = su.SudokuSolver(method=x)
                self.p.init_puzzle(EASY_PUZZLE)
                self.assertTrue(solver.solve(self.p))
                self.assertTrue(self.p.is_solved())

                self.p.init_puzzle(HARD_PUZZLE)
                self.assertTrue(solver.solve(self.p))
                self.assertTrue(self.p.is_solved())
        return

    def test_all_solvers_all_sizes(self):
        """Solvers can solve different sizes of puzzles"""
        for m in su.SOLVERS:
            solver = su.SudokuSolver(method=m)
            for i, puz in enumerate(TEST_PUZZLE_STRINGS):
                # Skip backtracking on larger puzzles
                if m == 'backtracking' and len(puz) > 81:
                    continue

                with self.subTest(f"Method {m}; Puzzle {i} (len={len(puz)})"):
                    p = su.SudokuPuzzle(starting_grid=ls.from_string(puz))
                    s = su.SudokuPuzzle(starting_grid=ls.from_string(TEST_SOLUTION_STRINGS[i]))
                    self.assertTrue(p.is_valid())
                    self.assertFalse(p.is_solved())
                    self.assertTrue(solver.solve(p))
                    self.assertTrue(p.is_solved())
                    self.assertEqual(str(s), str(p))
        return

    def test_all_solvers_unsolvable_puzzles(self):
        """Test all solvers on how they handle unsolvable puzzles"""
        for m in su.SOLVERS:
            solver = su.SudokuSolver(method=m)
            for i, puz in enumerate(UNSOLVABLE_STRINGS):
                with self.subTest(f"Method {m}; Unsolvable puzzle {i}"):
                    # These "unsolvable" puzzles are still valid initially
                    self.p.init_puzzle(ls.from_string(puz))
                    self.assertTrue(self.p.is_valid())
                    self.assertFalse(self.p.is_solved())

                    # Check method correctly reports it cannot be solved
                    self.assertFalse(solver.solve(self.p))

                    # Solver should leave puzzle in valid, but unsolved state
                    self.assertTrue(self.p.is_valid())
                    self.assertFalse(self.p.is_solved())
        return

    def test_all_solvers_multisolution_puzzles(self):
        """Test all solvers on how they handle puzzles with multiple solutions"""
        for m in su.SOLVERS:
            solver = su.SudokuSolver(method=m)
            for i, puz in enumerate(MULTI_SOLUTION_STRINGS):
                with self.subTest(f"Method {m}; Multi-solution puzzle {i}"):
                    # Failure here would be test data error
                    self.p.init_puzzle(ls.from_string(puz))
                    self.assertTrue(self.p.is_valid())
                    self.assertFalse(self.p.is_solved())

                    # Requirement is to return *a* solution
                    self.assertTrue(solver.solve(self.p))
                    self.assertTrue(self.p.is_solved())

                    # TODO: Mechanism to report multiple solutions? SAT could
                    # do it. Others might take too long.
        return

    @unittest.skipUnless(os.environ.get('SUDOKU_LONG_TESTS', False), 'Long running test')
    def test_all_solvers_all_puzzles(self):
        """Test that all available solvers can solve all test puzzles in sudoku.py"""
        for x in su.SOLVERS:
            if x == 'backtracking':
                continue
            solver = su.SudokuSolver(method=x)
            for p in su.SAMPLE_PUZZLES:
                with self.subTest(f"Method {x} on puzzle {p['label']}"):
                    puz = su.SudokuPuzzle(starting_grid=ls.from_string(p['puzzle']))
                    self.assertTrue(solver.solve(puz))
                    self.assertTrue(puz.is_solved())
        return


if __name__ == "__main__":
    unittest.main()
