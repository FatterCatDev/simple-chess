import unittest

from game.game import Game
from gui.controller import GameController


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


if __name__ == "__main__":
    unittest.main()
