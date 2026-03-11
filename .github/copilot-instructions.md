# Simple Chess - Project Configuration

## Project Type: Python Project for Learning

## Current Status Snapshot

- Core chess engine rules are implemented (including castling, en passant, promotion, draw rules, and undo).
- SAN-lite notation export/import is implemented and tested.
- JSON save/load file support is implemented through the controller and GUI.
- Replay controls API (`replay_start`, `replay_next`, `replay_previous`, `replay_end`) is implemented.
- Tkinter GUI prototype is implemented (board rendering, piece sprites, selection/move flow, legal move highlighting, undo/reset, promotion dialog, move history sidebar, file menu actions).
- Replay UI is fully functional: static history display, position highlighting during navigation, move restrictions mid-replay.
- Windows title bar theming follows personalization app mode, and the app uses a custom dark top menu bar.
- Current test status: `101 passed, 0 failed`.

### Completed Steps:

- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	- Project Type: Python project
	- Purpose: Learning
	- Language: Python
	- Status: Complete

- [x] Scaffold the Project
	- Created src/ directory for source code
	- Created main.py as entry point
	- Created requirements.txt for dependencies
	- Created .gitignore for version control
	- Created README.md with setup instructions

- [x] Install Required Extensions
	- No Python-specific extensions required (Python extension is built-in to VS Code)

- [x] Compile/Verify the Project
	- Project structure verified
	- No compilation needed for Python
	- Ready to run with: python src/main.py
	- Tests run with: python -m unittest discover -s src/tests

- [x] Ensure Documentation is Complete
	- README.md created with setup and running instructions
	- Project documentation is complete and up to date

## Getting Started

1. Navigate to the project directory
2. Create a Python virtual environment: `python -m venv venv`
3. Activate the virtual environment (on Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the project: `python src/main.py`

## Project Structure

```
Simple Chess/
├── src/
│   ├── ai/
│   ├── game/
│   ├── gui/
│   ├── tests/
│   ├── utils/
│   └── main.py          # Main entry point
├── .github/
│   └── copilot-instructions.md  # This file
├── DESIGN.md
├── SAVE_LOAD_FEATURE.md
├── requirements.txt     # Project dependencies
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```
