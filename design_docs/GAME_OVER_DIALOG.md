# Game Over Dialog — Feature Design Document

## 1. Overview

When a game ends by checkmate, stalemate, or a draw rule, the app shows a modal dialog automatically so the result is clearly visible.

---

## 2. Trigger Conditions

The dialog fires **immediately after a move** that ends the game. It must satisfy **all** of
the following conditions before opening:

| Condition | Source in `get_state()` |
|---|---|
| The game is over | `state["game_over"] == True` |
| Replay mode is not active | `state["replay"]["active"] == False` |

The replay guard is strict: if replay mode is active, the dialog must **not** open.
The dialog only opens during a **live** game.

---

## 3. Result Messages

The dialog headline changes depending on the outcome. Use the following rules:

| Outcome | How to detect | Message |
|---|---|---|
| Checkmate — White wins | `game_over == True`, `is_draw == False`, `current_turn == "W"` | `"Checkmate! White wins!"` |
| Checkmate — Black wins | `game_over == True`, `is_draw == False`, `current_turn == "B"` | `"Checkmate! Black wins!"` |
| Stalemate | `game_over == True`, `is_draw == True`, `draw_reason == "Stalemate"` | `"Stalemate! The game is a draw."` |
| Threefold repetition | `game_over == True`, `is_draw == True`, `draw_reason == "Threefold repetition"` | `"Draw due to threefold repetition."` |
| Fifty-move rule | `game_over == True`, `is_draw == True`, `draw_reason == "Fifty-move rule"` | `"Draw due to fifty-move rule."` |
| Insufficient material | `game_over == True`, `is_draw == True`, `draw_reason == "Insufficient material"` | `"Draw due to insufficient material."` |
| Unknown draw | `game_over == True`, `is_draw == True`, any other `draw_reason` | `"Draw!"` |

> **Why `current_turn`?** The engine does **not** advance the turn after a mating move.
> `current_turn` stays on the player who just delivered mate. So `current_turn == "W"`
> means white made the last move and won; `current_turn == "B"` means black made the last
> move and won.

---

## 4. Dialog Layout

```
┌─────────────────────────────────────────────────────┐
│              Checkmate — White wins!                 │  ← tk.Label  font Helvetica 16 bold  fg #FFF
│                                                      │
│  [ New Game ]  [ Save Game ]  [ Replay ]  [ Close ]  │  ← four ttk.Buttons  style "Replay.TButton"
└─────────────────────────────────────────────────────┘
```

All four buttons sit in a single `tk.Frame` row, packed left-to-right with equal
`padx=8` spacing. The frame is centered by packing it with no `fill` or `expand`.

- Window title: `"Game Over"`
- Background: `GLOBAL_BUTTON_STYLE["primary"]`  (`#221D33`)
- Non-resizable: `resizable(False, False)`
- Modal (blocks input to main window): `grab_set()`
- Centered over the main window (see Section 6)

---

## 5. Button Behaviour

### New Game
Calls the existing `handle_new()` function (same function wired to `Game > New` in the
menu bar) and then closes the dialog.

### Save Game
Calls the existing `handle_save()` function directly (same function wired to `Game > Save`
in the menu bar). The dialog stays open after saving so the user can still choose what to
do next. If the user cancels the file-picker without saving, nothing happens — the dialog
remains open.

### Replay
Closes the dialog first, then calls the existing `handle_replay_start()` function. This
resets the board to the starting position of the just-played game and enters replay mode,
allowing the user to step through every move using the existing replay controls (`|<`, `<`,
`>`, `>|`).

> `handle_replay_start()` already calls `game_controller.replay_start()`, which builds
> the replay notation from the current move history before resetting the board —
> so no new controller logic is required.

### Close
Destroys the dialog only. The board stays frozen in the final position. The user can still
use the menu bar to start a new game or load a file.

### Window Close (X button)
Behaves the same as **Close** — destroy the dialog, do nothing else.

---

## 6. Positioning

Center the dialog over the main window using this formula after calling `update_idletasks()`:

```
x = main.winfo_x() + (main.winfo_width()  - dialog.winfo_width())  // 2
y = main.winfo_y() + (main.winfo_height() - dialog.winfo_height()) // 2
dialog.geometry(f"+{x}+{y}")
```

---

## 7. Where to Integrate in `app.py`

### 7a. Define the function

Add a new inner function `show_game_over_dialog(message)` inside `run_app()`, near the
existing `ask_promotion_choice` helper. It follows the same `tk.Toplevel` pattern.

### 7b. Call the function

Inside `refresh_board()`, **after** the board and status label have already been updated,
add a check at the very end of the function:

```python
if state["game_over"] and not state["replay"]["active"]:
    show_game_over_dialog(_build_game_over_message(state))
```

The helper `_build_game_over_message(state)` (a plain inner function, not a method)
translates the state dict into one of the strings from the table in Section 3.

> `refresh_board()` is already called after every move, undo, reset, and load — so there
> is no other place that needs to be touched.

### 7c. Guard against repeated calls

Add a module-level flag variable `game_over_dialog_shown = False` just before the main
event loop. Set it to `True` when the dialog opens, and reset it to `False` in
`handle_new()` and during a successful `handle_load()`. The check in `refresh_board()`
should also gate on `not game_over_dialog_shown`.

---

## 8. Style Reference

Match the existing `ask_promotion_choice` dialog precisely:

| Element | Property |
|---|---|
| `tk.Toplevel` bg | `GLOBAL_BUTTON_STYLE["primary"]` |
| `tk.Label` bg | `GLOBAL_BUTTON_STYLE["primary"]` |
| `tk.Label` fg | `"#FFF"` |
| `tk.Label` font | `("Helvetica", 16, "bold")` for headline |
| `tk.Frame` bg | `GLOBAL_BUTTON_STYLE["primary"]` |
| Buttons | `ttk.Button` with `style="Replay.TButton"` |
| Button padding | `padx=10, pady=6` inside the button frame |
| Vertical padding | `pady=(16, 6)` for headline, `pady=(0, 16)` for button frame |

---

## 9. Files Changed

| File | Change |
|---|---|
| `src/gui/app.py` | Contains `show_game_over_dialog()`, `_build_game_over_message()`, `game_over_dialog_shown` flag; `refresh_board()` triggers dialog when game is over and not replaying |

No changes to `controller.py` or the game engine are needed — `handle_save()`,
`handle_replay_start()`, and `handle_new()` already exist in `app.py` and can be called
directly from within `show_game_over_dialog()`.

No changes to the game engine or controller are needed — all required data is already
exposed through `get_state()`.

---

## 10. Test Plan

Manual/UI verification is currently the primary validation path for this feature.
Automated tests in `src/tests/test_controller.py` validate state semantics used by the dialog trigger path.

| # | Scenario | Assert |
|---|---|---|
| 1 | Checkmate — white delivers mate | `game_over == True`, `is_draw == False`, `current_turn == "W"` |
| 2 | Checkmate — black delivers mate | `game_over == True`, `is_draw == False`, `current_turn == "B"` |
| 3 | Stalemate | `game_over == True`, `is_draw == True`, `draw_reason == "Stalemate"` |
| 4 | Game over during live play (not replay) | `replay["active"] == False` |
| 5 | Game over at end of replay (`replay_index == total`) | `replay["active"] == True`, `replay["index"] == replay["total"]` — dialog must **not** open |
| 6 | Game over mid-replay (`replay_index < total`) | `replay["active"] == True`, `replay["index"] < replay["total"]` — dialog must **not** open |
| 7 | After Replay button: replay mode is active | Call `replay_start()` on a finished game; assert `replay["active"] == True`, `replay["index"] == 0`, `replay["total"] > 0` |
| 8 | After Replay button: board is at starting position | After `replay_start()`, assert no pieces have moved from their start squares |

Test 6 is the most important: it directly verifies the replay-mode guard.

---

## 11. Acceptance Criteria

- [x] Dialog opens after checkmate in a live game
- [x] Dialog opens after stalemate in a live game
- [x] Dialog opens after each draw rule in a live game
- [x] Dialog does **not** open while replay is active (including replay end)
- [x] **New Game** button resets the board and closes the dialog
- [x] **Save Game** button opens the file-picker; dialog stays open regardless of whether the user saves or cancels
- [x] **Replay** button closes the dialog and enters replay mode at move 0 of the finished game
- [x] **Close** button closes only the dialog; board stays frozen
- [x] Dialog headline matches the outcome exactly (Section 3 table)
- [x] Dialog visual style matches the rest of the app (dark bg, white text, `Replay.TButton`)
- [x] Dialog is centered over the main window
- [x] Dialog is modal (main window is unclickable while dialog is open)
- [x] Opening a new game resets the dialog-shown flag so it can fire again next game
- [x] Dialog logic is implemented and wired in live gameplay flow
- [x] Dialog does not open while replay is active
- [x] Dialog supports New Game / Save Game / Replay / Close actions

---

## 12. Manual QA Checklist (Runbook)

Use this table when validating a new change to dialog behavior.

| ID | Setup | Action | Expected |
|---|---|---|---|
| QA-01 | Start a new game | Play Fool's Mate (`f3 e5 g4 Qh4#`) | Dialog opens once with checkmate winner message |
| QA-02 | From a fresh game | Play into stalemate | Dialog opens once with stalemate/draw message |
| QA-03 | Finish any game and open dialog | Click **Save Game**, cancel file picker | Dialog remains open; board position unchanged |
| QA-04 | Finish any game and open dialog | Click **Save Game**, save successfully | Success feedback appears; dialog remains open |
| QA-05 | Finish any game and open dialog | Click **Replay** | Dialog closes; replay mode starts at `0/total` |
| QA-06 | In replay mode after QA-05 | Step with `<`, `>`, `>|` | Dialog never opens while replay is active |
| QA-07 | In replay mode at `index == total` | Stay in replay mode | Dialog still does not open |
| QA-08 | Finish any game and open dialog | Click **New Game** | Dialog closes; board resets; feature can trigger again next game |
| QA-09 | Finish any game and open dialog | Click **Close** or title bar `X` | Dialog closes only; final board stays visible |
| QA-10 | Finish any game then load a different game | Use `Game > Load` | Dialog flag resets; dialog behavior is correct for loaded game |
