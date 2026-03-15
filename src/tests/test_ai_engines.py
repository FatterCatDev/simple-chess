import unittest
from game.game import Game
from game.piece import King, Queen, Rook, Knight, Bishop, Pawn
from utils.constants import COLOR
from ai.simple_heuristic_ai import SimpleHeuristicAI
from ai.sim_adapter import ai_state_to_game, game_to_ai_state, generate_legal_moves_on_state


class TestSimpleHeuristicAI(unittest.TestCase):

    def _clear_board(self, game):
        for sq in list(game.board.board.keys()):
            game.board.remove_piece_at(sq)

    def _assert_state_move_parity(self, game):
        live_moves = sorted(game.get_all_valid_moves(game.current_turn))
        state = game_to_ai_state(game)
        state_moves = sorted(generate_legal_moves_on_state(state))
        self.assertEqual(state_moves, live_moves)

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

    def test_difficulty2_get_move_does_not_mutate_live_game_state(self):
        game = Game()
        ai = SimpleHeuristicAI(difficulty=2)

        pre_snapshot = game.board.get_board_snapshot()
        pre_turn = game.current_turn
        pre_last_move = game.last_move
        pre_move_history_len = len(game.move_history)
        pre_game_over = game.game_over
        pre_draw = game.is_draw
        pre_check = game.is_in_check

        move = ai.get_move(game)

        self.assertIsNotNone(move)
        self.assertEqual(game.board.get_board_snapshot(), pre_snapshot)
        self.assertEqual(game.current_turn, pre_turn)
        self.assertEqual(game.last_move, pre_last_move)
        self.assertEqual(len(game.move_history), pre_move_history_len)
        self.assertEqual(game.game_over, pre_game_over)
        self.assertEqual(game.is_draw, pre_draw)
        self.assertEqual(game.is_in_check, pre_check)

    def test_difficulty2_survives_repeated_live_turns(self):
        game = Game()
        white_ai = SimpleHeuristicAI(difficulty=2)
        black_ai = SimpleHeuristicAI(difficulty=2)

        for _ in range(30):
            if game.game_over:
                break

            current_ai = white_ai if game.current_turn == COLOR["white"] else black_ai
            move = current_ai.get_move(game)
            self.assertIsNotNone(move)

            from_sq, to_sq = move
            self.assertIn(to_sq, game.get_legal_moves(from_sq))
            game.make_move(from_sq, to_sq)

        self.assertGreater(len(game.move_history), 0)

    def test_ai_state_round_trip_preserves_position(self):
        game = Game()
        game.make_move("e2", "e4")
        game.make_move("e7", "e5")

        state = game_to_ai_state(game)
        rebuilt = ai_state_to_game(state)

        self.assertEqual(rebuilt.board.get_board_snapshot(), game.board.get_board_snapshot())
        self.assertEqual(rebuilt.current_turn, game.current_turn)
        self.assertEqual(rebuilt.is_in_check, game.is_in_check)
        self.assertEqual(rebuilt.halfmove_clock, game.halfmove_clock)
        self.assertEqual(rebuilt.last_move["from"], game.last_move["from"])
        self.assertEqual(rebuilt.last_move["to"], game.last_move["to"])

    def test_state_legal_move_parity_from_start(self):
        game = Game()
        self._assert_state_move_parity(game)

    def test_state_legal_move_parity_after_opening_sequence(self):
        game = Game()
        sequence = [
            ("e2", "e4"),
            ("e7", "e5"),
            ("g1", "f3"),
            ("b8", "c6"),
            ("f1", "c4"),
            ("g8", "f6"),
            ("d2", "d3"),
            ("f8", "c5"),
        ]
        for from_sq, to_sq in sequence:
            game.make_move(from_sq, to_sq)

        self._assert_state_move_parity(game)

    def test_state_legal_move_parity_after_en_passant_window(self):
        game = Game()
        sequence = [
            ("e2", "e4"),
            ("a7", "a6"),
            ("e4", "e5"),
            ("d7", "d5"),
        ]
        for from_sq, to_sq in sequence:
            game.make_move(from_sq, to_sq)

        self._assert_state_move_parity(game)

    def test_state_legal_move_parity_when_castling_available(self):
        game = Game()
        sequence = [
            ("e2", "e4"),
            ("a7", "a6"),
            ("g1", "f3"),
            ("a6", "a5"),
            ("f1", "c4"),
            ("h7", "h6"),
        ]
        for from_sq, to_sq in sequence:
            game.make_move(from_sq, to_sq)

        self._assert_state_move_parity(game)
        self.assertIn(("e1", "g1"), game.get_all_valid_moves(game.current_turn))

    def test_state_legal_move_parity_after_king_moves_no_castle(self):
        game = Game()
        sequence = [
            ("e2", "e4"),
            ("a7", "a6"),
            ("e1", "e2"),
            ("a6", "a5"),
            ("e2", "e1"),
            ("a5", "a4"),
        ]
        for from_sq, to_sq in sequence:
            game.make_move(from_sq, to_sq)

        self._assert_state_move_parity(game)
        self.assertNotIn(("e1", "g1"), game.get_all_valid_moves(game.current_turn))
        self.assertNotIn(("e1", "c1"), game.get_all_valid_moves(game.current_turn))


if __name__ == "__main__":
    unittest.main()
