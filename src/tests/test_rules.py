import unittest

from game.board import ChessBoard
from game.standard_chess_rules import StandardChessRules
from utils.constants import COLOR


class TestStandardChessRules(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.rules = StandardChessRules(self.board)

    def test_pawn_initial_two_square_move_valid(self):
        self.assertTrue(self.rules.is_valid_move("e2", "e4"))

    def test_pawn_cannot_move_backwards(self):
        self.assertFalse(self.rules.is_valid_move("e2", "e1"))

    def test_knight_can_jump_over_pieces(self):
        self.assertTrue(self.rules.is_valid_move("b1", "c3"))

    def test_bishop_move_blocked_by_piece(self):
        self.assertFalse(self.rules.is_valid_move("c1", "h6"))

    def test_queen_move_blocked_by_piece(self):
        self.assertFalse(self.rules.is_valid_move("d1", "d3"))

    def test_cannot_capture_own_piece(self):
        self.assertFalse(self.rules.is_valid_move("b1", "d2"))

    def test_king_cannot_move_two_squares_without_castling(self):
        self.assertFalse(self.rules.is_valid_move("e1", "e3"))

    def test_black_pawn_initial_two_square_move_valid(self):
        self.assertTrue(self.rules.is_valid_move("e7", "e5"))

    def test_move_to_out_of_bounds_rank_is_invalid(self):
        self.assertFalse(self.rules.is_valid_move("e2", "e9"))

    def test_knight_move_off_board_is_invalid(self):
        self.assertFalse(self.rules.is_valid_move("b1", "a0"))

    @unittest.skip("TODO: Implement castling logic")
    def test_castling_kingside_white(self):
        self.assertTrue(self.rules.is_valid_move("e1", "g1"))

    def test_en_passant_white_capture_valid(self):
        """Test white pawn can capture black pawn en passant."""
        # Clear the board and set up en passant scenario
        for pos in ["e2", "d7"]:
            self.board.remove_piece_at(pos)
        
        # White pawn on e5, black pawn moves d7 to d5 (two squares)
        from game.piece import Pawn
        white_pawn = Pawn(COLOR["white"], "e5")
        black_pawn = Pawn(COLOR["black"], "d5")
        self.board.set_piece_at("e5", white_pawn)
        self.board.set_piece_at("d5", black_pawn)
        
        # Build last_move for black pawn moving d7->d5
        last_move = {
            "piece_type": "P",
            "piece_color": COLOR["black"],
            "from": "d7",
            "to": "d5",
            "captured_piece": None,
            "was_two_square_pawn_move": True
        }
        
        # White pawn should be able to capture en passant to d6
        self.assertTrue(self.rules.is_valid_move("e5", "d6", last_move))

    def test_en_passant_black_capture_valid(self):
        """Test black pawn can capture white pawn en passant."""
        # Clear the board and set up en passant scenario
        for pos in ["e7", "d2"]:
            self.board.remove_piece_at(pos)
        
        # Black pawn on e4, white pawn moves d2 to d4 (two squares)
        from game.piece import Pawn
        black_pawn = Pawn(COLOR["black"], "e4")
        white_pawn = Pawn(COLOR["white"], "d4")
        self.board.set_piece_at("e4", black_pawn)
        self.board.set_piece_at("d4", white_pawn)
        
        # Build last_move for white pawn moving d2->d4
        last_move = {
            "piece_type": "P",
            "piece_color": COLOR["white"],
            "from": "d2",
            "to": "d4",
            "captured_piece": None,
            "was_two_square_pawn_move": True
        }
        
        # Black pawn should be able to capture en passant to d3
        self.assertTrue(self.rules.is_valid_move("e4", "d3", last_move))

    def test_en_passant_not_valid_without_two_square_move(self):
        """Test en passant is not valid if last move wasn't a two-square pawn advance."""
        # Clear the board
        for pos in ["e2", "d7"]:
            self.board.remove_piece_at(pos)
        
        from game.piece import Pawn
        white_pawn = Pawn(COLOR["white"], "e5")
        black_pawn = Pawn(COLOR["black"], "d5")
        self.board.set_piece_at("e5", white_pawn)
        self.board.set_piece_at("d5", black_pawn)
        
        # Last move was NOT a two-square advance
        last_move = {
            "piece_type": "P",
            "piece_color": COLOR["black"],
            "from": "d6",
            "to": "d5",
            "captured_piece": None,
            "was_two_square_pawn_move": False
        }
        
        # Should not allow en passant
        self.assertFalse(self.rules.is_valid_move("e5", "d6", last_move))

    def test_en_passant_not_valid_without_last_move(self):
        """Test en passant is not valid if no last move exists."""
        # Clear the board
        for pos in ["e2", "d7"]:
            self.board.remove_piece_at(pos)
        
        from game.piece import Pawn
        white_pawn = Pawn(COLOR["white"], "e5")
        black_pawn = Pawn(COLOR["black"], "d5")
        self.board.set_piece_at("e5", white_pawn)
        self.board.set_piece_at("d5", black_pawn)
        
        # No last move
        self.assertFalse(self.rules.is_valid_move("e5", "d6", None))

    @unittest.skip("TODO: Implement promotion handling")
    def test_pawn_promotion_trigger(self):
        self.assertTrue(self.rules.is_valid_move("e7", "e8"))


if __name__ == "__main__":
    unittest.main()
