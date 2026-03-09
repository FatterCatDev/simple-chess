import unittest

from game.game import Game
from game.piece import Rook, King, Pawn, Queen, Bishop
from utils.constants import COLOR


class TestGameFlow(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_initial_turn_is_white(self):
        self.assertEqual(self.game.current_turn, COLOR["white"])

    def test_valid_move_updates_board_and_turn(self):
        self.game.make_move("e2", "e4")

        moved_piece = self.game.board.get_piece_at("e4")
        self.assertIsNotNone(moved_piece)
        self.assertEqual(moved_piece.type, "P")
        self.assertEqual(moved_piece.color, COLOR["white"])
        self.assertTrue(moved_piece.has_moved)

        self.assertIsNone(self.game.board.get_piece_at("e2"))
        self.assertEqual(self.game.current_turn, COLOR["black"])

    def test_wrong_turn_raises_error(self):
        with self.assertRaises(ValueError):
            self.game.make_move("e7", "e5")

    def test_illegal_rook_move_raises_error(self):
        with self.assertRaises(ValueError):
            self.game.make_move("a1", "a3")

    def test_pawn_capture_updates_board_state(self):
        # e2 -> e4, d7 -> d5, e4 x d5
        self.game.make_move("e2", "e4")
        self.game.make_move("d7", "d5")
        self.game.make_move("e4", "d5")

        captured_square_piece = self.game.board.get_piece_at("d5")
        self.assertIsNotNone(captured_square_piece)
        self.assertEqual(captured_square_piece.type, "P")
        self.assertEqual(captured_square_piece.color, COLOR["white"])
        self.assertIsNone(self.game.board.get_piece_at("e4"))

    def test_turn_sequence_across_multiple_moves(self):
        self.assertEqual(self.game.current_turn, COLOR["white"])

        self.game.make_move("g1", "f3")
        self.assertEqual(self.game.current_turn, COLOR["black"])

        self.game.make_move("g8", "f6")
        self.assertEqual(self.game.current_turn, COLOR["white"])

        self.game.make_move("b1", "c3")
        self.assertEqual(self.game.current_turn, COLOR["black"])

    def test_invalid_destination_square_raises_error(self):
        with self.assertRaises(ValueError):
            self.game.make_move("e2", "e9")


class TestCheckDetection(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_in_check_false_in_start_position(self):
        """No check at game start."""
        self.assertFalse(self.game.in_check(COLOR["white"]))
        self.assertFalse(self.game.in_check(COLOR["black"]))

    def test_in_check_true_rook_on_open_file(self):
        """White king in check from black rook on open file."""
        # Clear board and set up check scenario
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # Place white king on e1, black rook on e8, black king on a8
        white_king = King(COLOR["white"], "e1")
        black_rook = Rook(COLOR["black"], "e8")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        self.assertTrue(self.game.in_check(COLOR["white"]))
        self.assertFalse(self.game.in_check(COLOR["black"]))

    def test_in_check_false_when_attack_blocked(self):
        """White king NOT in check when pawn blocks rook."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # Place white king on e1, black rook on e8, white pawn on e4, black king on a8
        white_king = King(COLOR["white"], "e1")
        black_rook = Rook(COLOR["black"], "e8")
        white_pawn = Pawn(COLOR["white"], "e4")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("e4", white_pawn)
        self.game.board.set_piece_at("a8", black_king)
        
        self.assertFalse(self.game.in_check(COLOR["white"]))
        self.assertFalse(self.game.in_check(COLOR["black"]))


class TestCheckmateDetection(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_back_rank_checkmate(self):
        """Test back rank checkmate scenario: trapped king with pawns blocking escape."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # Set up back rank mate: King on g1, trapped by pawns on f2/g2/h2
        # Black rook on a1 delivers checkmate along the first rank
        white_king = King(COLOR["white"], "g1")
        white_pawn_f = Pawn(COLOR["white"], "f2")
        white_pawn_g = Pawn(COLOR["white"], "g2")
        white_pawn_h = Pawn(COLOR["white"], "h2")
        black_rook = Rook(COLOR["black"], "a1")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("g1", white_king)
        self.game.board.set_piece_at("f2", white_pawn_f)
        self.game.board.set_piece_at("g2", white_pawn_g)
        self.game.board.set_piece_at("h2", white_pawn_h)
        self.game.board.set_piece_at("a1", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        # White is in check
        self.assertTrue(self.game.in_check(COLOR["white"]))
        
        # White is in checkmate - no legal moves escape check
        self.assertTrue(self.game.checkmate(COLOR["white"]))

    def test_check_but_not_checkmate(self):
        """Test scenario where king is in check but can escape."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # White king on e4 in open space, black rook on e8
        white_king = King(COLOR["white"], "e4")
        black_rook = Rook(COLOR["black"], "e8")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e4", white_king)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        # White is in check
        self.assertTrue(self.game.in_check(COLOR["white"]))
        
        # But it's not checkmate - king can escape to d3, d4, d5, f3, f4, f5
        self.assertFalse(self.game.checkmate(COLOR["white"]))

    def test_cannot_move_into_check(self):
        """Test that you cannot make a move that puts your own king in check."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # White king on e1, white rook on e2 (blocking check), black rook on e8
        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "e2")
        black_rook = Rook(COLOR["black"], "e8")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e2", white_rook)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        self.game.current_turn = COLOR["white"]
        
        # Rook is blocking check - moving it away from the file should be illegal
        with self.assertRaises(ValueError) as context:
            self.game.make_move("e2", "a2")
        
        # Should raise error about exposing king to check
        self.assertIn("check", str(context.exception).lower())

    def test_block_check_with_piece(self):
        """Test that you can block a check by interposing a piece."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # White king on e1, white rook on a4, black rook on e8
        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "a4")
        black_rook = Rook(COLOR["black"], "e8")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a4", white_rook)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        self.game.current_turn = COLOR["white"]
        
        # White is in check
        self.assertTrue(self.game.in_check(COLOR["white"]))
        
        # White can block by moving rook to e4
        self.game.make_move("a4", "e4")
        
        # Turn switches to black - white is no longer in check
        self.assertEqual(self.game.current_turn, COLOR["black"])

    def test_capture_checking_piece(self):
        """Test escaping check by capturing the attacking piece."""
        # Clear board
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)
        
        # White king on e1, white queen on d7, black rook on e8
        white_king = King(COLOR["white"], "e1")
        white_queen = Queen(COLOR["white"], "d7")
        black_rook = Rook(COLOR["black"], "e8")
        black_king = King(COLOR["black"], "a8")
        
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("d7", white_queen)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.board.set_piece_at("a8", black_king)
        
        self.game.current_turn = COLOR["white"]
        
        # White is in check (rook attacks king on e-file)
        self.assertTrue(self.game.in_check(COLOR["white"]))
        
        # White can capture the checking rook with queen (diagonal move)
        self.game.make_move("d7", "e8")
        
        # Check is resolved
        self.assertEqual(self.game.current_turn, COLOR["black"])

    def test_fools_mate(self):
        """Test the shortest checkmate: Fool's Mate in 2 moves."""
        # f3, e5, g4, Qh4# 
        self.game.make_move("f2", "f3")
        self.game.make_move("e7", "e5")
        self.game.make_move("g2", "g4")
        self.game.make_move("d8", "h4")
        
        # White should be in checkmate
        self.assertTrue(self.game.in_check(COLOR["white"]))
        self.assertTrue(self.game.checkmate(COLOR["white"]))
        self.assertTrue(self.game.game_over)

    def test_scholars_mate(self):
        """Test Scholar's Mate checkmate pattern."""
        # e4, e5, Bc4, Nc6, Qh5, Nf6?, Qxf7#
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        self.game.make_move("f1", "c4")
        self.game.make_move("b8", "c6")
        self.game.make_move("d1", "h5")
        self.game.make_move("g8", "f6")
        self.game.make_move("h5", "f7")
        
        # Black should be in checkmate
        self.assertTrue(self.game.in_check(COLOR["black"]))
        self.assertTrue(self.game.checkmate(COLOR["black"]))
        self.assertTrue(self.game.game_over)


class TestStalemateDetection(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_classic_stalemate_position(self):
        """Black to move: king on a8 with no legal moves, but not in check."""
        self._clear_board()

        black_king = King(COLOR["black"], "a8")
        white_king = King(COLOR["white"], "c6")
        white_queen = Queen(COLOR["white"], "c7")

        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("c6", white_king)
        self.game.board.set_piece_at("c7", white_queen)

        self.assertFalse(self.game.in_check(COLOR["black"]))
        self.assertTrue(self.game.stalemate(COLOR["black"]))
        self.assertEqual(self.game.get_all_valid_moves(COLOR["black"]), [])

    def test_not_stalemate_when_legal_move_exists(self):
        """Black has at least one legal move (a8 -> a7), so no stalemate."""
        self._clear_board()

        black_king = King(COLOR["black"], "a8")
        white_king = King(COLOR["white"], "c6")
        white_queen = Queen(COLOR["white"], "d6")

        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("c6", white_king)
        self.game.board.set_piece_at("d6", white_queen)

        self.assertFalse(self.game.in_check(COLOR["black"]))
        self.assertFalse(self.game.stalemate(COLOR["black"]))

    def test_make_move_sets_game_over_on_stalemate(self):
        """A move that creates stalemate should end the game without switching turns."""
        self._clear_board()

        black_king = King(COLOR["black"], "a8")
        white_king = King(COLOR["white"], "c6")
        white_queen = Queen(COLOR["white"], "d7")

        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("c6", white_king)
        self.game.board.set_piece_at("d7", white_queen)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("d7", "c7")

        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.is_draw)
        self.assertEqual(self.game.draw_reason, "Stalemate")
        self.assertTrue(self.game.stalemate(COLOR["black"]))
        self.assertEqual(self.game.current_turn, COLOR["white"])

    def test_cannot_move_after_stalemate_draw(self):
        """After stalemate ends the game, further moves are rejected."""
        self._clear_board()

        black_king = King(COLOR["black"], "a8")
        white_king = King(COLOR["white"], "c6")
        white_queen = Queen(COLOR["white"], "d7")

        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("c6", white_king)
        self.game.board.set_piece_at("d7", white_queen)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("d7", "c7")

        with self.assertRaises(ValueError) as context:
            self.game.make_move("a8", "a7")

        self.assertIn("game is over", str(context.exception).lower())

    def test_stalemate_false_when_in_check(self):
        """A checked king cannot be stalemated."""
        self._clear_board()

        black_king = King(COLOR["black"], "a8")
        white_king = King(COLOR["white"], "c6")
        white_rook = Rook(COLOR["white"], "a1")

        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("c6", white_king)
        self.game.board.set_piece_at("a1", white_rook)

        self.assertTrue(self.game.in_check(COLOR["black"]))
        self.assertFalse(self.game.stalemate(COLOR["black"]))


class TestCastling(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_white_kingside_castling_moves_both_pieces(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("e1", "g1")

        self.assertIsNone(self.game.board.get_piece_at("e1"))
        self.assertIsNone(self.game.board.get_piece_at("h1"))
        self.assertEqual(self.game.board.get_piece_at("g1").type, "K")
        self.assertEqual(self.game.board.get_piece_at("f1").type, "R")
        self.assertEqual(self.game.current_turn, COLOR["black"])

    def test_king_two_square_move_without_rook_is_invalid(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)
        self.game.current_turn = COLOR["white"]

        with self.assertRaises(ValueError):
            self.game.make_move("e1", "g1")

    def test_cannot_castle_through_attacked_square(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")
        black_pawn = Pawn(COLOR["black"], "g2")  # attacks f1

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("g2", black_pawn)
        self.game.current_turn = COLOR["white"]

        with self.assertRaises(ValueError):
            self.game.make_move("e1", "g1")

    def test_cannot_castle_while_in_check(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")
        black_rook = Rook(COLOR["black"], "e8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("e8", black_rook)
        self.game.current_turn = COLOR["white"]

        with self.assertRaises(ValueError):
            self.game.make_move("e1", "g1")

    def test_get_all_valid_moves_includes_castling(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)

        moves = self.game.get_all_valid_moves(COLOR["white"])

        self.assertIn(("e1", "g1"), moves)


class TestEnPassantExecution(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_white_en_passant_capture_removes_black_pawn(self):
        """Test white en passant actually removes the black pawn from the board."""
        self._clear_board()

        from game.piece import Pawn, King
        white_pawn = Pawn(COLOR["white"], "e5")
        black_pawn = Pawn(COLOR["black"], "d7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e5", white_pawn)
        self.game.board.set_piece_at("d7", black_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_king)

        white_pawn.has_moved = True  # Mark as already moved to e5

        # Black moves d7 -> d5 (two squares)
        self.game.current_turn = COLOR["black"]
        self.game.make_move("d7", "d5")

        # Verify black pawn is on d5
        self.assertIsNotNone(self.game.board.get_piece_at("d5"))
        self.assertEqual(self.game.board.get_piece_at("d5").type, "P")
        self.assertEqual(self.game.board.get_piece_at("d5").color, COLOR["black"])

        # White captures en passant: e5 -> d6
        self.game.make_move("e5", "d6")

        # Verify white pawn is on d6
        self.assertIsNotNone(self.game.board.get_piece_at("d6"))
        self.assertEqual(self.game.board.get_piece_at("d6").type, "P")
        self.assertEqual(self.game.board.get_piece_at("d6").color, COLOR["white"])

        # Verify black pawn was removed from d5
        self.assertIsNone(self.game.board.get_piece_at("d5"))

        # Verify e5 is now empty
        self.assertIsNone(self.game.board.get_piece_at("e5"))

    def test_black_en_passant_capture_removes_white_pawn(self):
        """Test black en passant actually removes the white pawn from the board."""
        self._clear_board()

        from game.piece import Pawn, King
        black_pawn = Pawn(COLOR["black"], "e4")
        white_pawn = Pawn(COLOR["white"], "d2")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e4", black_pawn)
        self.game.board.set_piece_at("d2", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_king)

        black_pawn.has_moved = True  # Mark as already moved to e4

        # White moves d2 -> d4 (two squares)
        self.game.current_turn = COLOR["white"]
        self.game.make_move("d2", "d4")

        # Black captures en passant: e4 -> d3
        self.game.make_move("e4", "d3")

        # Verify black pawn is on d3
        self.assertIsNotNone(self.game.board.get_piece_at("d3"))
        self.assertEqual(self.game.board.get_piece_at("d3").type, "P")
        self.assertEqual(self.game.board.get_piece_at("d3").color, COLOR["black"])

        # Verify white pawn was removed from d4
        self.assertIsNone(self.game.board.get_piece_at("d4"))


class TestPromotion(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_white_pawn_promotes_to_queen_on_8th_rank(self):
        """Test white pawn auto-promotes to queen when reaching 8th rank."""
        self._clear_board()

        from game.piece import Pawn, King
        white_pawn = Pawn(COLOR["white"], "e7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)  # Move black king out of the way

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        # Move pawn from e7 to e8 (promotion)
        self.game.make_move("e7", "e8")

        # Check that square now has a Queen
        promoted_piece = self.game.board.get_piece_at("e8")
        self.assertIsNotNone(promoted_piece)
        self.assertEqual(promoted_piece.type, "Q")
        self.assertEqual(promoted_piece.color, COLOR["white"])

    def test_black_pawn_promotes_to_queen_on_1st_rank(self):
        """Test black pawn auto-promotes to queen when reaching 1st rank."""
        self._clear_board()

        from game.piece import Pawn, King
        black_pawn = Pawn(COLOR["black"], "e2")
        white_king = King(COLOR["white"], "a1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e2", black_pawn)
        self.game.board.set_piece_at("a1", white_king)
        self.game.board.set_piece_at("e8", black_king)

        black_pawn.has_moved = True
        self.game.current_turn = COLOR["black"]

        # Move pawn from e2 to e1 (promotion)
        self.game.make_move("e2", "e1")

        # Check that square now has a Queen
        promoted_piece = self.game.board.get_piece_at("e1")
        self.assertIsNotNone(promoted_piece)
        self.assertEqual(promoted_piece.type, "Q")
        self.assertEqual(promoted_piece.color, COLOR["black"])

    def test_promotion_with_capture(self):
        """Test pawn can promote when capturing on promotion rank."""
        self._clear_board()

        from game.piece import Pawn, King, Rook
        white_pawn = Pawn(COLOR["white"], "e7")
        black_rook = Rook(COLOR["black"], "d8")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "h8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("d8", black_rook)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h8", black_king)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        # Capture rook and promote
        self.game.make_move("e7", "d8", "Q")

        # Check promotion happened
        promoted_piece = self.game.board.get_piece_at("d8")
        self.assertIsNotNone(promoted_piece)
        self.assertEqual(promoted_piece.type, "Q")
        self.assertEqual(promoted_piece.color, COLOR["white"])

    def test_promotion_to_knight(self):
        """Test pawn can promote to knight."""
        self._clear_board()

        from game.piece import Pawn, King
        white_pawn = Pawn(COLOR["white"], "e7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        # Promote to knight
        self.game.make_move("e7", "e8", "N")

        promoted_piece = self.game.board.get_piece_at("e8")
        self.assertEqual(promoted_piece.type, "N")

    def test_promotion_to_rook(self):
        """Test pawn can promote to rook."""
        self._clear_board()

        from game.piece import Pawn, King
        white_pawn = Pawn(COLOR["white"], "e7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        # Promote to rook
        self.game.make_move("e7", "e8", "R")

        promoted_piece = self.game.board.get_piece_at("e8")
        self.assertEqual(promoted_piece.type, "R")

    def test_promotion_to_bishop(self):
        """Test pawn can promote to bishop."""
        self._clear_board()

        from game.piece import Pawn, King
        white_pawn = Pawn(COLOR["white"], "e7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        # Promote to bishop
        self.game.make_move("e7", "e8", "B")

        promoted_piece = self.game.board.get_piece_at("e8")
        self.assertEqual(promoted_piece.type, "B")

    def test_en_passant_blocked_if_would_expose_king(self):
        """Test that en passant is rejected if it would expose the king to check."""
        self._clear_board()

        from game.piece import Pawn, King, Rook
        # White king on e5, white pawn on d5
        # Black pawn on c7, black rook on a5 (attacking along rank 5)
        white_king = King(COLOR["white"], "e5")
        white_pawn = Pawn(COLOR["white"], "d5")
        black_pawn = Pawn(COLOR["black"], "c7")
        black_rook = Rook(COLOR["black"], "a5")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e5", white_king)
        self.game.board.set_piece_at("d5", white_pawn)
        self.game.board.set_piece_at("c7", black_pawn)
        self.game.board.set_piece_at("a5", black_rook)
        self.game.board.set_piece_at("e8", black_king)

        white_pawn.has_moved = True

        # Black moves c7 -> c5 (two squares)
        self.game.current_turn = COLOR["black"]
        self.game.make_move("c7", "c5")

        # White tries en passant d5 -> c6, but this would expose king to rook on a5
        self.game.current_turn = COLOR["white"]
        
        # Verify pawn is still blocking the rook
        self.assertIsNotNone(self.game.board.get_piece_at("d5"))
        self.assertIsNotNone(self.game.board.get_piece_at("c5"))
        
        # This move should be rejected
        with self.assertRaises(ValueError) as context:
            self.game.make_move("d5", "c6")
        
        self.assertIn("check", str(context.exception).lower())
        
        # Verify board state is unchanged - black pawn still on c5
        self.assertIsNotNone(self.game.board.get_piece_at("c5"))
        self.assertEqual(self.game.board.get_piece_at("c5").type, "P")
        self.assertEqual(self.game.board.get_piece_at("c5").color, COLOR["black"])
        
        # Verify white pawn still on d5
        self.assertIsNotNone(self.game.board.get_piece_at("d5"))
        self.assertEqual(self.game.board.get_piece_at("d5").type, "P")


class TestMoveHistory(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_move_history_starts_empty(self):
        self.assertEqual(self.game.move_history, [])

    def test_make_move_returns_last_history_entry(self):
        move_info = self.game.make_move("e2", "e4")
        self.assertEqual(len(self.game.move_history), 1)
        self.assertEqual(move_info["from"], self.game.move_history[-1]["from"])
        self.assertEqual(move_info["to"], self.game.move_history[-1]["to"])
        self.assertIn("san", move_info)
        self.assertIn("was_castling", move_info)

    def test_move_history_records_basic_move_metadata(self):
        self.game.make_move("e2", "e4")
        entry = self.game.move_history[-1]

        self.assertEqual(entry["from"], "e2")
        self.assertEqual(entry["to"], "e4")
        self.assertEqual(entry["piece_type"], "P")
        self.assertEqual(entry["piece_color"], COLOR["white"])
        self.assertFalse(entry["was_castling"])
        self.assertFalse(entry["was_en_passant"])
        self.assertTrue(entry["was_two_square_pawn_move"])
        self.assertEqual(entry["current_turn"], COLOR["white"])

    def test_move_history_san_for_pawn_push(self):
        self.game.make_move("e2", "e4")
        self.assertEqual(self.game.move_history[-1]["san"], "e4")

    def test_move_history_san_for_kingside_castling(self):
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("e1", "g1")
        entry = self.game.move_history[-1]

        self.assertTrue(entry["was_castling"])
        self.assertEqual(entry["san"], "O-O")

    def test_move_history_san_for_en_passant(self):
        self._clear_board()

        white_pawn = Pawn(COLOR["white"], "e5")
        black_pawn = Pawn(COLOR["black"], "d7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("e5", white_pawn)
        self.game.board.set_piece_at("d7", black_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_king)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["black"]
        self.game.make_move("d7", "d5")

        self.game.make_move("e5", "d6")
        entry = self.game.move_history[-1]

        self.assertTrue(entry["was_en_passant"])
        self.assertEqual(entry["san"], "exd6 e.p.")

    def test_move_history_san_for_promotion(self):
        self._clear_board()

        white_pawn = Pawn(COLOR["white"], "e7")
        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "a8")
        black_rook = Rook(COLOR["black"], "h8")

        self.game.board.set_piece_at("e7", white_pawn)
        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("a8", black_king)
        self.game.board.set_piece_at("h8", black_rook)

        white_pawn.has_moved = True
        self.game.current_turn = COLOR["white"]

        self.game.make_move("e7", "e8", "N")
        self.assertEqual(self.game.move_history[-1]["san"], "e8=N")

    def test_move_history_san_marks_check_with_plus(self):
        """A move that gives check should include '+' suffix in SAN-lite."""
        self._clear_board()

        white_king = King(COLOR["white"], "a1")
        white_rook = Rook(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")

        self.game.board.set_piece_at("a1", white_king)
        self.game.board.set_piece_at("e1", white_rook)
        self.game.board.set_piece_at("e8", black_king)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("e1", "e7")

        self.assertTrue(self.game.in_check(COLOR["black"]))
        self.assertTrue(self.game.move_history[-1]["san"].endswith("+"))

    def test_move_history_san_marks_checkmate_with_hash(self):
        """A move that checkmates should include '#' suffix in SAN-lite."""
        self.game.make_move("f2", "f3")
        self.game.make_move("e7", "e5")
        self.game.make_move("g2", "g4")
        self.game.make_move("d8", "h4")

        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.checkmate(COLOR["white"]))
        self.assertTrue(self.game.move_history[-1]["san"].endswith("#"))


class TestNotationPersistence(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _assert_replay_matches_current_game(self):
        """Replay exported notation and assert SAN, turn, and board snapshot match."""
        notation_moves = self.game.export_notation()
        expected_san = [entry["san"] for entry in self.game.move_history]
        expected_snapshot = self.game.board.get_board_snapshot()
        expected_turn = self.game.current_turn

        replay_game = Game()
        replay_game.load_notation(notation_moves)

        replay_san = [entry["san"] for entry in replay_game.move_history]
        self.assertEqual(replay_san, expected_san)
        self.assertEqual(replay_game.board.get_board_snapshot(), expected_snapshot)
        self.assertEqual(replay_game.current_turn, expected_turn)
        return replay_game

    def test_export_notation_contains_recorded_san_moves(self):
        """Exported notation should include SAN moves in order."""
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        self.game.make_move("g1", "f3")

        notation_moves = self.game.export_notation()

        self.assertIsInstance(notation_moves, list)
        self.assertEqual(notation_moves, ["e4", "e5", "Nf3"])

    def test_export_import_round_trip_restores_state_and_history(self):
        """Loading exported notation should recreate board state and SAN history."""
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        self.game.make_move("g1", "f3")
        self.game.make_move("b8", "c6")

        expected_san = [entry["san"] for entry in self.game.move_history]
        expected_turn = self.game.current_turn
        expected_e4 = self.game.board.get_piece_at("e4")
        expected_e5 = self.game.board.get_piece_at("e5")
        expected_f3 = self.game.board.get_piece_at("f3")
        expected_c6 = self.game.board.get_piece_at("c6")

        notation_moves = self.game.export_notation()

        replay_game = Game()
        replay_game.load_notation(notation_moves)

        replay_san = [entry["san"] for entry in replay_game.move_history]
        self.assertEqual(replay_san, expected_san)
        self.assertEqual(replay_game.current_turn, expected_turn)

        replay_e4 = replay_game.board.get_piece_at("e4")
        replay_e5 = replay_game.board.get_piece_at("e5")
        replay_f3 = replay_game.board.get_piece_at("f3")
        replay_c6 = replay_game.board.get_piece_at("c6")

        self.assertIsNotNone(replay_e4)
        self.assertIsNotNone(replay_e5)
        self.assertIsNotNone(replay_f3)
        self.assertIsNotNone(replay_c6)

        self.assertEqual(replay_e4.type, expected_e4.type)
        self.assertEqual(replay_e5.type, expected_e5.type)
        self.assertEqual(replay_f3.type, expected_f3.type)
        self.assertEqual(replay_c6.type, expected_c6.type)

    def test_load_notation_rejects_non_list_input(self):
        """load_notation should validate input shape and item type."""
        with self.assertRaises(ValueError):
            self.game.load_notation("e4")

        with self.assertRaises(ValueError):
            self.game.load_notation(["e4", 123])

    def test_load_notation_replays_pawn_capture_sequence(self):
        """Replay should preserve pawn-capture SAN and final board state."""
        self.game.make_move("e2", "e4")
        self.game.make_move("d7", "d5")
        self.game.make_move("e4", "d5")

        replay_game = self._assert_replay_matches_current_game()
        self.assertIn("exd5", replay_game.export_notation())
        piece_on_d5 = replay_game.board.get_piece_at("d5")
        self.assertIsNotNone(piece_on_d5)
        self.assertEqual(piece_on_d5.type, "P")
        self.assertEqual(piece_on_d5.color, COLOR["white"])

    def test_load_notation_replays_en_passant_sequence(self):
        """Replay should support SAN-lite en passant with 'e.p.' suffix."""
        self.game.make_move("e2", "e4")
        self.game.make_move("a7", "a6")
        self.game.make_move("e4", "e5")
        self.game.make_move("d7", "d5")
        self.game.make_move("e5", "d6")

        replay_game = self._assert_replay_matches_current_game()
        self.assertIn("exd6 e.p.", replay_game.export_notation())
        self.assertIsNotNone(replay_game.board.get_piece_at("d6"))
        self.assertIsNone(replay_game.board.get_piece_at("d5"))

    def test_strip_san_suffixes_removes_ep_and_trailing_spaces(self):
        """SAN stripping should normalize en-passant notation for replay parsing."""
        clean_san, e_p_flag, promotion_type = self.game._strip_san_suffixes("exd6 e.p.")

        self.assertEqual(clean_san, "exd6")
        self.assertTrue(e_p_flag)
        self.assertIsNone(promotion_type)

    def test_load_notation_replays_castling_sequence(self):
        """Replaying SAN that includes castling should restore king/rook squares."""
        # Build a legal kingside-castling sequence for white.
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        self.game.make_move("g1", "f3")
        self.game.make_move("b8", "c6")
        self.game.make_move("f1", "e2")
        self.game.make_move("g8", "f6")
        self.game.make_move("e1", "g1")

        notation_moves = self.game.export_notation()
        expected_san = [entry["san"] for entry in self.game.move_history]

        replay_game = Game()
        replay_game.load_notation(notation_moves)

        replay_san = [entry["san"] for entry in replay_game.move_history]
        self.assertEqual(replay_san, expected_san)
        self.assertIn("O-O", replay_san)

        white_king = replay_game.board.get_piece_at("g1")
        white_rook = replay_game.board.get_piece_at("f1")
        self.assertIsNotNone(white_king)
        self.assertIsNotNone(white_rook)
        self.assertEqual(white_king.type, "K")
        self.assertEqual(white_rook.type, "R")

    def test_load_notation_replays_queenside_castling_sequence(self):
        """Replaying SAN with queenside castling should restore king/rook squares."""
        self.game.make_move("d2", "d4")
        self.game.make_move("d7", "d5")
        self.game.make_move("b1", "c3")
        self.game.make_move("b8", "c6")
        self.game.make_move("c1", "f4")
        self.game.make_move("g8", "f6")
        self.game.make_move("d1", "d2")
        self.game.make_move("e7", "e6")
        self.game.make_move("e1", "c1")

        replay_game = self._assert_replay_matches_current_game()
        self.assertIn("O-O-O", replay_game.export_notation())
        white_king = replay_game.board.get_piece_at("c1")
        white_rook = replay_game.board.get_piece_at("d1")
        self.assertIsNotNone(white_king)
        self.assertIsNotNone(white_rook)
        self.assertEqual(white_king.type, "K")
        self.assertEqual(white_rook.type, "R")

    def test_load_notation_replays_promotion_capture_sequence(self):
        """Replay should preserve SAN-lite capture promotion notation."""
        self.game.make_move("a2", "a4")
        self.game.make_move("h7", "h5")
        self.game.make_move("a4", "a5")
        self.game.make_move("h5", "h4")
        self.game.make_move("a5", "a6")
        self.game.make_move("h4", "h3")
        self.game.make_move("a6", "b7")
        self.game.make_move("h3", "g2")
        self.game.make_move("b7", "a8", promotion_choice="Q")

        replay_game = self._assert_replay_matches_current_game()
        last_san = replay_game.export_notation()[-1]
        self.assertIn("=Q", last_san)
        promoted_piece = replay_game.board.get_piece_at("a8")
        self.assertIsNotNone(promoted_piece)
        self.assertEqual(promoted_piece.type, "Q")
        self.assertEqual(promoted_piece.color, COLOR["white"])

    def test_load_notation_replays_checkmate_suffix(self):
        """Replay should parse SAN-lite '#' suffix and preserve game-over state."""
        self.game.make_move("f2", "f3")
        self.game.make_move("e7", "e5")
        self.game.make_move("g2", "g4")
        self.game.make_move("d8", "h4")

        replay_game = self._assert_replay_matches_current_game()
        self.assertTrue(replay_game.export_notation()[-1].endswith("#"))
        self.assertTrue(replay_game.game_over)


class TestUndoRegression(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def _clear_board(self):
        for square in self.game.board.board.keys():
            self.game.board.remove_piece_at(square)

    def test_undo_restore_captured_rook_has_moved_state(self):
        """Undo should restore captured piece metadata, including has_moved."""
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        black_king = King(COLOR["black"], "e8")
        white_rook = Rook(COLOR["white"], "h1")
        black_queen = Queen(COLOR["black"], "h2")
        white_pawn = Pawn(COLOR["white"], "a2")
        black_pawn = Pawn(COLOR["black"], "a7")

        # Simulate a rook that has already moved earlier in the game.
        white_rook.has_moved = True

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("e8", black_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("h2", black_queen)
        self.game.board.set_piece_at("a2", white_pawn)
        self.game.board.set_piece_at("a7", black_pawn)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("a2", "a3")
        self.game.make_move("h2", "h1")
        self.game.undo_move()

        restored_rook = self.game.board.get_piece_at("h1")
        self.assertIsNotNone(restored_rook)
        self.assertEqual(restored_rook.type, "R")
        self.assertTrue(restored_rook.has_moved)

    def test_undo_castling_resets_rook_has_moved_to_false(self):
        """After undoing castling, rook.has_moved should be False."""
        self._clear_board()

        white_king = King(COLOR["white"], "e1")
        white_rook = Rook(COLOR["white"], "h1")
        black_king = King(COLOR["black"], "a8")

        self.game.board.set_piece_at("e1", white_king)
        self.game.board.set_piece_at("h1", white_rook)
        self.game.board.set_piece_at("a8", black_king)
        self.game.current_turn = COLOR["white"]

        self.game.make_move("e1", "g1")

        castled_rook = self.game.board.get_piece_at("f1")
        self.assertIsNotNone(castled_rook)
        self.assertTrue(castled_rook.has_moved)

        self.game.undo_move()

        restored_rook = self.game.board.get_piece_at("h1")
        self.assertIsNotNone(restored_rook)
        self.assertEqual(restored_rook.type, "R")
        self.assertFalse(restored_rook.has_moved)


class TestResetGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_reset_game_clears_transient_flags(self):
        self.game.is_in_check = True
        self.game.piece_first_move_status = True

        self.game.reset_game()

        self.assertFalse(self.game.is_in_check)
        self.assertFalse(self.game.piece_first_move_status)

    def test_reset_game_restores_core_baseline_state(self):
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")

        self.game.reset_game()

        self.assertEqual(self.game.current_turn, COLOR["white"])
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.is_draw)
        self.assertIsNone(self.game.draw_reason)
        self.assertEqual(self.game.halfmove_clock, 0)
        self.assertEqual(self.game.position_history, [])
        self.assertIsNone(self.game.last_move)
        self.assertEqual(self.game.move_history, [])


class TestNotationReplayControls(unittest.TestCase):
    def setUp(self):
        # Build a short, legal move list we can replay.
        builder = Game()
        builder.make_move("e2", "e4")
        builder.make_move("e7", "e5")
        builder.make_move("g1", "f3")
        builder.make_move("b8", "c6")

        self.notation = builder.export_notation()
        self.final_snapshot = builder.board.get_board_snapshot()

        self.replay_game = Game()
        self.initial_snapshot = self.replay_game.board.get_board_snapshot()
        self.replay_game.load_notation(self.notation)

        # Snapshot after first ply for next/previous assertions.
        first_ply_game = Game()
        first_ply_game.make_move("e2", "e4")
        self.first_ply_snapshot = first_ply_game.board.get_board_snapshot()

    def test_replay_start_resets_to_initial_position(self):
        """replay_start should jump to move 0 initial board state."""
        self.replay_game.replay_start()
        self.assertEqual(self.replay_game.board.get_board_snapshot(), self.initial_snapshot)

    def test_replay_end_restores_final_position(self):
        """replay_end should jump to final board state from notation replay."""
        self.replay_game.replay_start()
        self.replay_game.replay_end()
        self.assertEqual(self.replay_game.board.get_board_snapshot(), self.final_snapshot)

    def test_replay_next_advances_one_ply(self):
        """replay_next should advance one move from the start position."""
        self.replay_game.replay_start()
        self.replay_game.replay_next()
        self.assertEqual(self.replay_game.board.get_board_snapshot(), self.first_ply_snapshot)

    def test_replay_previous_moves_back_one_ply(self):
        """replay_previous should move one ply backward from final state."""
        self.replay_game.replay_end()
        self.replay_game.replay_previous()

        expected = Game()
        expected.make_move("e2", "e4")
        expected.make_move("e7", "e5")
        expected.make_move("g1", "f3")
        self.assertEqual(self.replay_game.board.get_board_snapshot(), expected.board.get_board_snapshot())

    def test_replay_navigation_is_clamped_at_bounds(self):
        """Repeated previous/next at bounds should be safe and stable."""
        self.replay_game.replay_start()
        self.replay_game.replay_previous()
        self.assertEqual(self.replay_game.board.get_board_snapshot(), self.initial_snapshot)

        self.replay_game.replay_end()
        self.replay_game.replay_next()
        self.assertEqual(self.replay_game.board.get_board_snapshot(), self.final_snapshot)


if __name__ == "__main__":
    unittest.main()
