# Simple Chess

A learning project for building a chess game in Python.

## Current Status

- Core chess rules are implemented (including castling, en passant, promotion, check/checkmate/stalemate, and draw rules).
- SAN-lite notation export/import is implemented.
- JSON save/load is implemented through the GUI/controller.
- Replay controls are implemented (`replay_start`, `replay_next`, `replay_previous`, `replay_end`).
- Game over dialog is implemented (New Game / Save Game / Replay / Close).
- Game mode setup is implemented at startup and New Game:
   - Player vs Player
   - Player vs AI
   - AI vs AI
   - AI engine selection (Random AI, Simple Heuristic Easy/Hard)
   - Player color selection for PvAI (White/Black)
- Board orientation flips when PvAI player color is Black.
- Previous-move highlighting is implemented (`from` and `to` squares).
- Current automated test status: `139 passed, 2 failed`.

## Project Structure

```
Simple Chess/
├── src/
│   ├── ai/
│   ├── game/
│   ├── gui/
│   ├── tests/
│   ├── utils/
│   └── main.py
├── design_docs/
│   ├── OVERALL_DESIGN.md
│   ├── SAVE_LOAD_FEATURE.md
│   ├── AI_OPPONENT_FEATURE.md
│   ├── GAME_OVER_DIALOG.md
│   └── KNOWN_BUGS.md
├── .github/
│   └── copilot-instructions.md
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites

- Git
- Python 3.8 or higher
- `tkinter` available in your Python installation (included with standard Python installers)

### Clone and Install

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd "Simple Chess"
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Runtime Dependencies

- `Pillow` (required for loading chess piece PNG assets)
- `tkinter` (GUI toolkit; shipped with standard CPython builds)

If `pip install -r requirements.txt` fails because `tkinter` is missing:

- Windows/macOS Python.org installers: reinstall Python and ensure `tkinter` is included.
- Linux (Debian/Ubuntu): install `python3-tk` with your package manager.

### Running the Project

```bash
python src/main.py
```

### Running the GUI Prototype

```bash
# PowerShell (Windows)
$env:PYTHONPATH="src"
python -m gui.app
```

```bash
# macOS/Linux
PYTHONPATH=src python -m gui.app
```

### Running Tests

```bash
python -m unittest discover -s src/tests
```

Current result in this workspace:
- `139 passed, 2 failed`
- Failing tests are both in `test_rules.py` and expect out-of-bounds moves to return `False` instead of raising `ValueError`.

## Development

This is a learning project. Feel free to experiment and expand the codebase.

## Rules Notes

- Threefold repetition uses a simplified rule in this project.
- A repeated position is detected from board piece placement snapshots.
- Castling rights and en passant rights are intentionally not included in repetition matching.
- SAN format is SAN-lite and includes custom draw/en passant suffix handling used internally by this project.

## Known Issues

- Current test suite is not fully green (`139 passed, 2 failed`).
- See `design_docs/KNOWN_BUGS.md` for tracked issues and status.

## License

This project is for educational purposes.
