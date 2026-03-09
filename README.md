# Simple Chess

A learning project for building a chess game in Python.

## Current Status

- Core chess rules are implemented and tested (movement, check/checkmate/stalemate, castling, en passant, promotion).
- Draw rules are implemented (threefold repetition using simplified board snapshots, fifty-move rule, insufficient material).
- SAN-lite notation is implemented for move history export/import (`export_notation`, `load_notation`).
- Notation replay-to-final-state is covered by tests, including captures, castling, promotion, en passant suffix parsing, and checkmate suffix parsing.
- Step-by-step replay controls (`replay_start`, `replay_next`, `replay_previous`, `replay_end`) are not implemented yet.
- Test status: `88 passed, 5 failed` (the 5 failures are replay-control API tests added intentionally as next TDD target).

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

- Python 3.8 or higher

### Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project

```bash
python src/main.py
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
