import unittest

from game.game import Game
from gui.controller import GameController
from utils.constants import COLOR


class TestGameControllerReplayRestrictions(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.controller = GameController(self.game)

    def test_try_move_blocked_while_replay_not_at_end(self):
        self.controller.selected_square = "e2"
        self.game.replay_active = True
        self.game.replay_notation = ["e4", "e5"]
        self.game.replay_index = 1

        result = self.controller.try_move("e4")

        self.assertFalse(result)
        self.assertEqual(
            self.controller.last_error,
            "Cannot make moves while not at the end of replaying.",
        )
        self.assertIsNotNone(self.game.board.get_piece_at("e2"))
        self.assertIsNone(self.game.board.get_piece_at("e4"))
        self.assertTrue(self.game.replay_active)
        self.assertEqual(self.game.replay_index, 1)
        self.assertEqual(self.game.replay_notation, ["e4", "e5"])

    def test_try_move_allowed_at_replay_end_and_clears_replay_state(self):
        self.controller.selected_square = "e2"
        self.game.replay_active = True
        self.game.replay_notation = ["e4", "e5"]
        self.game.replay_index = 2

        result = self.controller.try_move("e4")

        self.assertTrue(result)
        self.assertIsNone(self.controller.selected_square)
        self.assertFalse(self.game.replay_active)
        self.assertEqual(self.game.replay_index, 0)
        self.assertEqual(self.game.replay_notation, [])
        self.assertIsNone(self.game.board.get_piece_at("e2"))
        self.assertIsNotNone(self.game.board.get_piece_at("e4"))

    def test_failed_move_at_replay_end_does_not_clear_replay_state(self):
        self.controller.selected_square = "e2"
        self.game.replay_active = True
        self.game.replay_notation = ["e4", "e5"]
        self.game.replay_index = 2

        result = self.controller.try_move("e5")

        self.assertFalse(result)
        self.assertTrue(self.game.replay_active)
        self.assertEqual(self.game.replay_index, 2)
        self.assertEqual(self.game.replay_notation, ["e4", "e5"])
        self.assertIn("Invalid move", self.controller.last_error)


class TestGameOverDialogState(unittest.TestCase):
    """
    Verify that get_state() surfaces the correct data for the game-over dialog
    after each end-game scenario, and that the replay guard behaves correctly.
    """

    def setUp(self):
        self.game = Game()
        self.controller = GameController(self.game)

    # ------------------------------------------------------------------
    # Helper: play Fool's Mate (black queen mates white, 4 moves)
    # Result: game_over=True, is_draw=False, current_turn="W" (white mated)
    # ------------------------------------------------------------------
    def _play_fools_mate(self):
        self.controller.selected_square = "f2"
        self.controller.try_move("f3")
        self.controller.selected_square = "e7"
        self.controller.try_move("e5")
        self.controller.selected_square = "g2"
        self.controller.try_move("g4")
        self.controller.selected_square = "d8"
        self.controller.try_move("h4")

    # ------------------------------------------------------------------
    # Helper: place pieces for a one-move stalemate.
    # Board: WKd6, WQf6, BKh8 — white's turn.
    # Qf6→g6 leaves black king with no legal moves and not in check.
    # ------------------------------------------------------------------
    def _setup_one_move_stalemate(self):
        from game.piece import King, Queen
        for sq in list(self.game.board.board.keys()):
            self.game.board.remove_piece_at(sq)
        self.game.board.set_piece_at("d6", King(COLOR["white"], "d6"))
        self.game.board.set_piece_at("f6", Queen(COLOR["white"], "f6"))
        self.game.board.set_piece_at("h8", King(COLOR["black"], "h8"))
        self.game.current_turn = COLOR["white"]

    # ------------------------------------------------------------------
    # Test 1 — Checkmate: black delivers mate (Fool's Mate)
    # The engine does not advance the turn after a mating move.
    # current_turn stays on the winning player ("B" = black wins).
    # ------------------------------------------------------------------
    def test_checkmate_black_wins_state(self):
        self._play_fools_mate()
        state = self.controller.get_state()
        self.assertTrue(state["game_over"])
        self.assertFalse(state["is_draw"])
        self.assertEqual(state["current_turn"], COLOR["black"])   # black delivered mate

    # ------------------------------------------------------------------
    # Test 2 — Checkmate: white delivers mate (Scholar's Mate)
    # current_turn stays on the winning player ("W" = white wins).
    # ------------------------------------------------------------------
    def test_checkmate_white_wins_state(self):
        self.controller.selected_square = "e2"; self.controller.try_move("e4")
        self.controller.selected_square = "e7"; self.controller.try_move("e5")
        self.controller.selected_square = "f1"; self.controller.try_move("c4")
        self.controller.selected_square = "b8"; self.controller.try_move("c6")
        self.controller.selected_square = "d1"; self.controller.try_move("h5")
        self.controller.selected_square = "g8"; self.controller.try_move("f6")
        self.controller.selected_square = "h5"; self.controller.try_move("f7")
        state = self.controller.get_state()
        self.assertTrue(state["game_over"])
        self.assertFalse(state["is_draw"])
        self.assertEqual(state["current_turn"], COLOR["white"])   # white delivered mate

    # ------------------------------------------------------------------
    # Test 3 — Stalemate
    # ------------------------------------------------------------------
    def test_stalemate_state(self):
        self._setup_one_move_stalemate()
        self.controller.selected_square = "f6"
        self.controller.try_move("g6")
        state = self.controller.get_state()
        self.assertTrue(state["game_over"])
        self.assertTrue(state["is_draw"])
        self.assertEqual(state["draw_reason"], "Stalemate")

    # ------------------------------------------------------------------
    # Test 4 — Game over during live play: replay is not active
    # ------------------------------------------------------------------
    def test_game_over_live_play_replay_not_active(self):
        self._play_fools_mate()
        state = self.controller.get_state()
        self.assertTrue(state["game_over"])
        self.assertFalse(state["replay"]["active"])

    # ------------------------------------------------------------------
    # Test 5 — Game over at end of replay (index == total)
    # Dialog SHOULD open in this case.
    # ------------------------------------------------------------------
    def test_game_over_at_end_of_replay_dialog_should_open(self):
        self._play_fools_mate()
        self.controller.replay_start()   # enters replay, index=0
        self.controller.replay_end()     # advances to the last position
        state = self.controller.get_state()
        self.assertTrue(state["game_over"])
        self.assertTrue(state["replay"]["active"])
        self.assertEqual(state["replay"]["index"], state["replay"]["total"])

    # ------------------------------------------------------------------
    # Test 6 — Game over mid-replay (index < total)
    # Dialog must NOT open in this case.
    # ------------------------------------------------------------------
    def test_game_over_mid_replay_dialog_must_not_open(self):
        self._play_fools_mate()
        self.controller.replay_start()   # enters replay, index=0
        self.controller.replay_next()    # advance one step
        state = self.controller.get_state()
        # The dialog guard condition: skip if active AND index < total
        self.assertTrue(state["replay"]["active"])
        self.assertLess(state["replay"]["index"], state["replay"]["total"])

    # ------------------------------------------------------------------
    # Test 7 — After replay_start(): mode is active at index 0
    # ------------------------------------------------------------------
    def test_replay_start_after_game_over_enters_replay_mode(self):
        self._play_fools_mate()
        result = self.controller.replay_start()
        self.assertTrue(result)
        state = self.controller.get_state()
        self.assertTrue(state["replay"]["active"])
        self.assertEqual(state["replay"]["index"], 0)
        self.assertGreater(state["replay"]["total"], 0)

    # ------------------------------------------------------------------
    # Test 8 — After replay_start(): board is reset to starting position
    # ------------------------------------------------------------------
    def test_replay_start_resets_board_to_start(self):
        self._play_fools_mate()
        self.controller.replay_start()
        state = self.controller.get_state()
        # Standard starting squares that would have changed during Fool's Mate
        # should be empty, and home ranks should be restored.
        board = state["board"]
        # f3 and g4 were moved to during Fool's Mate — both should now be empty
        self.assertIsNone(board.get("f3"))
        self.assertIsNone(board.get("g4"))
        # f2 and g2 pawns should be back on their starting squares
        self.assertIsNotNone(board.get("f2"))
        self.assertIsNotNone(board.get("g2"))


if __name__ == "__main__":
    unittest.main()
