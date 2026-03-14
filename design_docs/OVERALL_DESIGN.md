# Simple Chess — Overall Design (Current State)

## 1. Project Overview

### 1.1 Purpose
This is a personal Python learning project focused on implementing a complete chess game with a Tkinter UI, replay support, and basic AI modes.

### 1.2 Current Scope
- Standard chess rules and special moves
- Draw rules (threefold repetition, fifty-move rule, insufficient material)
- SAN-lite notation export/import
- JSON save/load wrapper around SAN-lite move history
- Replay navigation (start/previous/next/end)
- Tkinter desktop UI with mode selection and AI support

---

## 2. Implemented Features

### 2.1 Engine and Rules
- Piece movement, blocking, capture rules
- Castling, en passant, promotion
- Check, checkmate, stalemate
- Draw rules and game-over state tracking
- Undo and reset

### 2.2 Notation / Persistence
- SAN-lite move recording in `Game`
- `export_notation()` and `load_notation(...)`
- Controller file I/O:
    - `save_notation_to_file(path)`
    - `load_notation_from_file(path)`
- Replayable history after load

### 2.3 GUI
- Board rendering with PNG sprites (Pillow)
- Click-to-select / click-to-move flow
- Legal move highlighting
- Previous move highlighting (`previous_from` / `previous_to`)
- Promotion dialog
- Move history sidebar with replay-position selection highlight
- Auto-hiding history scrollbar
- Replay control buttons (`|<`, `<`, `>`, `>|`)
- File menu actions: New / Save / Load
- Game over dialog (New Game / Save Game / Replay / Close)
- Windows dark title-bar integration

### 2.4 AI and Modes
- `AIEngine` interface
- Built-in `RandomAI`
- Built-in `SimpleHeuristicAI` (easy/hard levels in GUI)
- Game setup dialog supports:
    - Player vs Player
    - Player vs AI
    - AI vs AI
- PvAI player-color selection (White/Black)
- Board orientation flips when player chooses Black in PvAI
- AI can move first on startup/new game when the chosen side is AI-controlled

---

## 3. Architecture

### 3.1 Layers
- **GUI**: `src/gui/app.py` (Tkinter UI, dialogs, rendering)
- **Controller**: `src/gui/controller.py` (UI-facing game API, replay state, save/load)
- **Game Logic**: `src/game/game.py`, `src/game/standard_chess_rules.py`
- **Board/Pieces**: `src/game/board.py`, `src/game/piece.py`
- **AI**: `src/ai/ai.py`, `src/ai/simple_heuristic_ai.py`

### 3.2 Runtime Flow
User action → `GameController` → `Game`/rules validation → state update → optional AI move (`should_ai_move`/`make_ai_move`) → GUI refresh.

---

## 4. Testing Status

### 4.1 Current Automated Result
- `139 passed, 2 failed`

### 4.2 Current Failing Tests
- `tests.test_rules.TestStandardChessRules.test_move_to_out_of_bounds_rank_is_invalid`
- `tests.test_rules.TestStandardChessRules.test_knight_move_off_board_is_invalid`

Both currently fail because invalid destination squares (for example `e9`, `a0`) raise `ValueError` from board bounds validation instead of returning `False`.

---

## 5. Open Items

- Rules/Help dialog is not implemented in the GUI.
- Replay does not show a dedicated move-number label separate from the status text.
- Stockfish/UCI integration is not implemented yet.

See `design_docs/KNOWN_BUGS.md` for tracked bug-level details.

