# Simple Chess

A learning project for building a chess game in Python.

## Current Status

- Core chess rules are implemented and tested (movement, check/checkmate/stalemate, castling, en passant, promotion).
- Draw rules are implemented (threefold repetition using simplified board snapshots, fifty-move rule, insufficient material).
- SAN-lite notation is implemented for move history export/import (`export_notation`, `load_notation`).
- Save/load to JSON file is implemented through the GUI/controller (`save_notation_to_file`, `load_notation_from_file`).
- Notation replay-to-final-state is covered by tests, including captures, castling, promotion, en passant suffix parsing, and checkmate suffix parsing.
- Step-by-step replay controls are implemented (`replay_start`, `replay_next`, `replay_previous`, `replay_end`).
- Tkinter GUI prototype is implemented with:
    - dark-aware Windows title bar support and custom dark top menu bar
   - centered 8x8 board
   - piece sprite rendering from PNG assets
   - click-to-select / click-to-move interaction
   - legal move highlighting (including castling destinations)
    - promotion choice dialog
    - status banner, undo, and reset controls
    - save/load/new actions in the File menu
   - replay navigation controls (|< < > >|)
   - move history sidebar with replay position highlighting
    - auto-hiding styled scrollbar for long history lists
   - static history display during replay (content frozen, highlight moves)
 - Test status: `101 passed, 0 failed`.

## Project Structure

```
simple-chess/
├── src/
│   ├── ai/
│   ├── game/
│   ├── gui/
│   ├── tests/
│   ├── utils/
│   └── main.py
├── DESIGN.md
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

## Development

This is a learning project. Feel free to experiment and expand the codebase.

## Rules Notes

- Threefold repetition uses a simplified rule in this project.
- A repeated position is detected from board piece placement snapshots.
- Castling rights and en passant rights are intentionally not included in repetition matching.
- SAN format is SAN-lite and includes custom draw/en passant suffix handling used internally by this project.

## License

This project is for educational purposes.
