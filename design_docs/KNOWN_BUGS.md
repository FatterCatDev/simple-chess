# Simple Chess — Known Bugs

This document tracks bugs and unintended behaviors discovered during development or testing. Each entry includes a description, reproduction steps, and current status.

---

## Bug Template

```
### BUG-XXX: Short description

- **Area:** gui / game / ai / controller / tests
- **Severity:** Low / Medium / High / Critical
- **Status:** Open / In Progress / Fixed / Won't Fix
- **Reported:** YYYY-MM-DD

**Description:**
What is wrong and what is the expected behavior.

**Steps to Reproduce:**
1. Step one
2. Step two
3. Observed result vs expected result

**Notes:**
Any extra context, workarounds, or related code pointers.
```

---

## Open Bugs

### BUG-007: Out-of-bounds target squares raise exception instead of returning False

- **Area:** game/rules
- **Severity:** Medium
- **Status:** Open
- **Reported:** 2026-03-14

**Description:**
`StandardChessRules.is_valid_move()` currently raises `ValueError` for destinations like `e9`/`a0` because board occupancy checks call `ChessBoard.is_position_occupied()`, which raises on invalid positions. Existing tests expect these cases to return `False`.

**Steps to Reproduce:**
1. Run `python -m unittest discover -s src/tests`.
2. Observe failures in `test_move_to_out_of_bounds_rank_is_invalid` and `test_knight_move_off_board_is_invalid`.
3. Both fail with `ValueError: Invalid position`.

**Notes:**
Current workspace test result: `139 passed, 2 failed`.

### BUG-006: Save during replay only saves moves up to current replay position

- **Area:** controller
- **Severity:** Medium
- **Status:** Fixed
- **Reported:** 2026-03-13
- **Fixed:** 2026-03-13

**Description:**
When saving a game while mid-replay, `save_notation_to_file` called `game.export_notation()`, which reads `game.move_history`. During replay, `move_history` only contains moves replayed so far, so the saved file was truncated at the current replay position rather than containing the full game.

**Steps to Reproduce:**
1. Load a saved game (enters replay mode).
2. Step partway through the replay (e.g., move 5 of 30).
3. Save the game via File → Save.
4. Open the saved file — it only contains moves 1–5.

**Fix:**
In `GameController.save_notation_to_file()`, check `game.replay_active` and use `game.replay_notation` (the full move list) instead of `game.export_notation()` when replay is active.

---

## Fixed Bugs

### BUG-001: Threefold repetition does not account for castling rights or en passant state

- **Area:** game
- **Severity:** Low
- **Status:** Won't Fix
- **Reported:** 2026-03-13

**Description:**
The threefold repetition check compares board piece placement only. FIDE rules require that castling availability and en passant rights also be identical for two positions to be considered the same. This project intentionally simplifies this rule.

**Notes:**
Documented in `OVERALL_DESIGN.md` Section 5.3 as a known design simplification.

---

### BUG-002: "Show current move number and notation during replay" not implemented

- **Area:** gui
- **Severity:** Low
- **Status:** Open
- **Reported:** 2026-03-13

**Description:**
During replay mode, the move list highlights the current position, but there is no dedicated label showing the current move number (e.g., "Move 14 / 40"). This was a planned item in Phase 2.6 of the implementation roadmap.

**Steps to Reproduce:**
1. Load a saved game file.
2. Use the replay controls (`|<`, `<`, `>`, `>|`) to step through moves.
3. Observe that no move counter is displayed next to the board.

**Notes:**
Tracked as an open item in `OVERALL_DESIGN.md` Phase 2.6: `[ ] Show current move number and notation during replay`.

---

### BUG-003: No game-over dialog after checkmate or stalemate

- **Area:** gui
- **Severity:** Medium
- **Status:** Fixed
- **Reported:** 2026-03-13
- **Fixed:** 2026-03-14

**Description:**
When the game ends by checkmate, stalemate, or a draw rule, the status label updates correctly but no dialog box appears to announce the result.

**Fix:**
`show_game_over_dialog(message)` and `_build_game_over_message(state)` added to `app.py`. The dialog fires at the end of `refresh_board()` whenever `state["game_over"] and not state["replay"]["active"]`. A `game_over_dialog_shown` flag prevents the dialog from re-opening after it has been dismissed. The dialog offers four buttons: New Game, Save Game, Replay, and Close.

---

### BUG-004: No Rules/Help dialog available in-app

- **Area:** gui
- **Severity:** Low
- **Status:** Open
- **Reported:** 2026-03-13

**Description:**
The UI design specifies a Help button that opens a dialog showing game rules and piece movements, but this has not been implemented. There is currently no way to access help from within the app.

**Notes:**
Tracked in `OVERALL_DESIGN.md` Phase 3: `[ ] Add Rules/Help dialog`.

---

### BUG-005: Game mode is hardcoded to Player vs RandomAI (Black)

- **Area:** gui
- **Severity:** Medium
- **Status:** Fixed
- **Reported:** 2026-03-13
- **Fixed:** 2026-03-14

**Description:**
`app.py` always creates a `RandomAI` as the Black opponent on startup and on "New Game". There is no way to switch to Player vs Player or to choose a different AI engine without editing the source code.

**Steps to Reproduce:**
1. Launch the application.
2. Observe that Black is always played by the AI with no option to disable it.
3. Click "New Game" — same hardcoded setup is used.

**Fix:**
A `show_mode_dialog()` Toplevel dialog is now shown on application startup and before every "New Game". The dialog presents three radio-button options (PvP, PvAI, AIvAI) and uses the selection to wire `GameController` with the correct AI instances via `mode_select()`. The `current_mode` variable tracks the selected mode across calls.

---

### BUG-008: Previous move highlighting style gets overwritten in board refresh

- **Area:** gui
- **Severity:** Medium
- **Status:** Fixed
- **Reported:** 2026-03-14
- **Fixed:** 2026-03-14

**Description:**
Previous move squares (`previous_from`, `previous_to`) were styled first, then overwritten by the default style branch in a second independent highlight block.

**Fix:**
`refresh_board()` now uses one chained highlight priority flow (selected → legal move → previous from/to → default), so previous-move styles persist correctly.

---
