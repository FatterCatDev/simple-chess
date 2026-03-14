import unittest
from game.game import Game
from game.piece import King, Queen, Rook, Knight, Bishop, Pawn
from utils.constants import COLOR
from ai.simple_heuristic_ai import SimpleHeuristicAI


class TestSimpleHeuristicAI(unittest.TestCase):

    def _clear_board(self, game):
        for sq in list(game.board.board.keys()):
            game.board.remove_piece_at(sq)

    # ------------------------------------------------------------------
    # Basic contract
    # ------------------------------------------------------------------

    def test_name_contains_simple_heuristic_ai(self):
        self.assertIn("Simple Heuristic AI", SimpleHeuristicAI().name)

    def test_difficulty1_returns_legal_move_from_start(self):
        game = Game()
        ai = SimpleHeuristicAI(difficulty=1)
        move = ai.get_move(game)
        self.assertIsNotNone(move)
        from_sq, to_sq = move
        self.assertIn(to_sq, game.get_legal_moves(from_sq))

    def test_difficulty2_returns_legal_move_from_start(self):
        game = Game()
        ai = SimpleHeuristicAI(difficulty=2)
        move = ai.get_move(game)
        self.assertIsNotNone(move)
        from_sq, to_sq = move
        self.assertIn(to_sq, game.get_legal_moves(from_sq))

    def test_returns_none_when_no_pieces_for_current_player(self):
        """If current player has no pieces, returns None."""
        game = Game()
        self._clear_board(game)
        # No pieces at all — _collect_all_moves returns []
        ai = SimpleHeuristicAI(difficulty=1)
        self.assertIsNone(ai.get_move(game))

    # ------------------------------------------------------------------
    # Difficulty 1 — greedy heuristic
    # ------------------------------------------------------------------

    def test_difficulty1_captures_undefended_piece(self):
        """Queen should capture the undefended rook rather than make a quiet move."""
        game = Game()
        self._clear_board(game)
        game.board.set_piece_at("a1", King(COLOR["white"], "a1"))
        game.board.set_piece_at("d1", Queen(COLOR["white"], "d1"))
        game.board.set_piece_at("d8", Rook(COLOR["black"], "d8"))   # undefended
        game.board.set_piece_at("h8", King(COLOR["black"], "h8"))
        game.current_turn = COLOR["white"]

        move = SimpleHeuristicAI(difficulty=1).get_move(game)
        self.assertEqual(move, ("d1", "d8"))

    def test_difficulty1_avoids_moving_into_attacked_square(self):
        """The engine should not move a piece to a square where it will be lost for free."""
        # Knight on b1 can only go to a3, c3 (both attacked by queen on c5, score -3 each)
        # or d2 (safe, score 0). Engine must pick a move with score >= 0.
        game = Game()
        self._clear_board(game)
        game.board.set_piece_at("a1", King(COLOR["white"], "a1"))
        game.board.set_piece_at("b1", Knight(COLOR["white"], "b1"))
        game.board.set_piece_at("c5", Queen(COLOR["black"], "c5"))  # attacks a3 and c3
        game.board.set_piece_at("h8", King(COLOR["black"], "h8"))
        game.current_turn = COLOR["white"]

        move = SimpleHeuristicAI(difficulty=1).get_move(game)
        from_sq, to_sq = move
        # Whatever move is chosen, the destination must not be hanging (score should be >= 0)
        score = SimpleHeuristicAI(difficulty=1)._evaluate_move(game, from_sq, to_sq)
        self.assertGreaterEqual(score, 0)

    def test_difficulty1_prefers_higher_value_capture(self):
        """Given a choice between capturing a pawn and capturing a queen, pick the queen."""
        # Pawn on a4 is reachable diagonally from d1 (+1).
        # Queen on d8 is reachable straight up the d-file (+9); nothing blocks the path.
        game = Game()
        self._clear_board(game)
        game.board.set_piece_at("a1", King(COLOR["white"], "a1"))
        game.board.set_piece_at("d1", Queen(COLOR["white"], "d1"))
        game.board.set_piece_at("a4", Pawn(COLOR["black"], "a4"))    # undefended pawn (+1), diagonal
        game.board.set_piece_at("d8", Queen(COLOR["black"], "d8"))   # undefended queen (+9), straight
        game.board.set_piece_at("h8", King(COLOR["black"], "h8"))
        game.current_turn = COLOR["white"]

        move = SimpleHeuristicAI(difficulty=1).get_move(game)
        self.assertEqual(move, ("d1", "d8"))

    # ------------------------------------------------------------------
    # Difficulty 2 — lookahead
    # ------------------------------------------------------------------

    def test_difficulty2_finds_checkmate_in_one(self):
        """Scholar's Mate: white queen on h5 should deliver Qxf7#."""
        game = Game()
        game.make_move("e2", "e4")
        game.make_move("e7", "e5")
        game.make_move("f1", "c4")
        game.make_move("b8", "c6")
        game.make_move("d1", "h5")
        game.make_move("g8", "f6")
        # White to move; Qxf7 is checkmate

        move = SimpleHeuristicAI(difficulty=2).get_move(game)
        self.assertEqual(move, ("h5", "f7"))


if __name__ == "__main__":
    unittest.main()
