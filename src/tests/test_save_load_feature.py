import json
import os
import tempfile
import unittest
from copy import deepcopy

from game.game import Game
from game.piece import King, Pawn, Queen, Rook
from gui.controller import GameController
from utils.constants import COLOR


class TestSaveLoadFeature(unittest.TestCase):
    """Spec-driven tests for SAN-lite Save/Load file flows."""

    def setUp(self):
        self.game = Game()
        self.controller = GameController(self.game)

    def _save_path(self, filename="save.json"):
        tmpdir = tempfile.mkdtemp()
        return os.path.join(tmpdir, filename)

    def _require_controller_api(self):
        self.assertTrue(
            hasattr(self.controller, "save_notation_to_file"),
            "Expected GameController.save_notation_to_file(file_path) to exist.",
        )
        self.assertTrue(
            hasattr(self.controller, "load_notation_from_file"),
            "Expected GameController.load_notation_from_file(file_path) to exist.",
        )

    def _play_basic_opening(self):
        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        self.game.make_move("g1", "f3")
        self.game.make_move("b8", "c6")

    def _clear_board(self, game):
        for square in game.board.board.keys():
            game.board.remove_piece_at(square)

    def _read_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _board_signature(self, game):
        return {
            square: (piece.color + piece.type if piece else None)
            for square, piece in game.board.board.items()
        }

    def test_save_blocked_when_no_moves(self):
        self._require_controller_api()
        save_path = self._save_path("empty_game.json")

        ok = self.controller.save_notation_to_file(save_path)

        self.assertFalse(ok)
        self.assertEqual(self.controller.last_error, "No moves to save.")
        self.assertFalse(os.path.exists(save_path))

    def test_save_mid_game_writes_full_san_lite_list_in_order(self):
        self._require_controller_api()
        self._play_basic_opening()
        expected_moves = self.game.export_notation()
        save_path = self._save_path("mid_game.json")

        ok = self.controller.save_notation_to_file(save_path)

        self.assertTrue(ok)
        payload = self._read_json(save_path)
        self.assertEqual(payload.get("format"), "san-lite-list")
        self.assertEqual(payload.get("version"), 1)
        self.assertEqual(payload.get("moves"), expected_moves)

    def test_load_valid_payload_reconstructs_final_position(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("e7", "e5")
        source_game.make_move("g1", "f3")
        source_game.make_move("b8", "c6")
        source_moves = source_game.export_notation()
        expected_board = {
            square: (
                piece.color[0].lower() + piece.type[0].upper() if piece else None
            )
            for square, piece in source_game.board.board.items()
        }

        save_path = self._save_path("load_valid.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1, "moves": source_moves}, f)

        target_controller = GameController(Game())
        self.assertTrue(
            hasattr(target_controller, "load_notation_from_file"),
            "Expected GameController.load_notation_from_file(file_path) to exist.",
        )

        ok = target_controller.load_notation_from_file(save_path)

        self.assertTrue(ok)
        self.assertEqual(target_controller.build_board_state(), expected_board)

    def test_load_castling_payload_reconstructs_king_and_rook_positions(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("e7", "e5")
        source_game.make_move("g1", "f3")
        source_game.make_move("b8", "c6")
        source_game.make_move("f1", "e2")
        source_game.make_move("g8", "f6")
        source_game.make_move("e1", "g1")

        save_path = self._save_path("castling.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {"format": "san-lite-list", "version": 1, "moves": source_game.export_notation()},
                f,
            )

        target_game = Game()
        target_controller = GameController(target_game)

        ok = target_controller.load_notation_from_file(save_path)

        self.assertTrue(ok)
        self.assertEqual(target_game.board.get_piece_at("g1").type, "K")
        self.assertEqual(target_game.board.get_piece_at("f1").type, "R")

    def test_load_en_passant_payload_reconstructs_capture_state(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("a7", "a6")
        source_game.make_move("e4", "e5")
        source_game.make_move("d7", "d5")
        source_game.make_move("e5", "d6")

        save_path = self._save_path("en_passant.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {"format": "san-lite-list", "version": 1, "moves": source_game.export_notation()},
                f,
            )

        target_game = Game()
        target_controller = GameController(target_game)

        ok = target_controller.load_notation_from_file(save_path)

        self.assertTrue(ok)
        self.assertIsNotNone(target_game.board.get_piece_at("d6"))
        self.assertIsNone(target_game.board.get_piece_at("d5"))

    def test_load_checkmate_suffix_payload_parses_successfully(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("f2", "f3")
        source_game.make_move("e7", "e5")
        source_game.make_move("g2", "g4")
        source_game.make_move("d8", "h4")

        saved_moves = source_game.export_notation()
        self.assertTrue(saved_moves[-1].endswith("#"))

        save_path = self._save_path("checkmate_suffix.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1, "moves": saved_moves}, f)

        target_game = Game()
        target_controller = GameController(target_game)

        ok = target_controller.load_notation_from_file(save_path)

        self.assertTrue(ok)
        self.assertTrue(target_game.game_over)

    def test_replay_navigation_works_after_load(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("e7", "e5")
        source_game.make_move("g1", "f3")
        source_game.make_move("b8", "c6")

        save_path = self._save_path("replay_after_load.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {"format": "san-lite-list", "version": 1, "moves": source_game.export_notation()},
                f,
            )

        target_controller = GameController(Game())
        ok = target_controller.load_notation_from_file(save_path)
        self.assertTrue(ok)

        self.assertTrue(target_controller.replay_start())
        self.assertEqual(target_controller.game.replay_index, 0)
        self.assertTrue(target_controller.replay_next())
        self.assertEqual(target_controller.game.replay_index, 1)
        self.assertTrue(target_controller.replay_previous())
        self.assertEqual(target_controller.game.replay_index, 0)
        self.assertTrue(target_controller.replay_end())
        self.assertEqual(
            target_controller.game.replay_index,
            len(target_controller.game.replay_notation),
        )

    def test_try_move_mid_replay_blocked_after_load(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("e7", "e5")

        save_path = self._save_path("blocked_mid_replay.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {"format": "san-lite-list", "version": 1, "moves": source_game.export_notation()},
                f,
            )

        target_controller = GameController(Game())
        self.assertTrue(target_controller.load_notation_from_file(save_path))

        self.assertTrue(target_controller.replay_start())
        self.assertTrue(target_controller.replay_next())

        target_controller.selected_square = "e2"
        moved = target_controller.try_move("e4")

        self.assertFalse(moved)
        self.assertEqual(
            target_controller.last_error,
            "Cannot make moves while not at the end of replaying.",
        )

    def test_move_at_replay_end_resumes_play_and_clears_replay(self):
        self._require_controller_api()

        source_game = Game()
        source_game.make_move("e2", "e4")
        source_game.make_move("e7", "e5")

        save_path = self._save_path("resume_after_load.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {"format": "san-lite-list", "version": 1, "moves": source_game.export_notation()},
                f,
            )

        target_game = Game()
        target_controller = GameController(target_game)
        self.assertTrue(target_controller.load_notation_from_file(save_path))

        self.assertTrue(target_controller.replay_end())
        target_controller.selected_square = "g1"
        moved = target_controller.try_move("f3")

        self.assertTrue(moved)
        self.assertFalse(target_game.replay_active)
        self.assertEqual(target_game.replay_index, 0)
        self.assertEqual(target_game.replay_notation, [])

    def test_load_rejects_non_list_moves_payload(self):
        self._require_controller_api()

        save_path = self._save_path("bad_shape.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1, "moves": "e4"}, f)

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)

    def test_load_rejects_empty_moves_payload(self):
        self._require_controller_api()

        save_path = self._save_path("empty_moves.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1, "moves": []}, f)

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)

    def test_load_rejects_missing_moves_field(self):
        self._require_controller_api()

        save_path = self._save_path("missing_moves.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1}, f)

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)

    def test_load_rejects_invalid_json(self):
        self._require_controller_api()

        save_path = self._save_path("invalid_json.json")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write('{"format": "san-lite-list", "version": 1, "moves": ["e4", }')

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)

    def test_load_rejects_missing_file(self):
        self._require_controller_api()

        save_path = self._save_path("does_not_exist.json")

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)

    def test_failed_load_does_not_mutate_current_board(self):
        self._require_controller_api()

        self.game.make_move("e2", "e4")
        self.game.make_move("e7", "e5")
        before_board = deepcopy(self._board_signature(self.game))
        before_turn = self.game.current_turn
        before_history = self.game.export_notation().copy()

        save_path = self._save_path("bad_payload.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({"format": "san-lite-list", "version": 1, "moves": "e4"}, f)

        ok = self.controller.load_notation_from_file(save_path)

        self.assertFalse(ok)
        self.assertIsNotNone(self.controller.last_error)
        self.assertEqual(self._board_signature(self.game), before_board)
        self.assertEqual(self.game.current_turn, before_turn)
        self.assertEqual(self.game.export_notation(), before_history)


if __name__ == "__main__":
    unittest.main()
