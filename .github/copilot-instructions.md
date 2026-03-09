# Simple Chess - Project Configuration

## Project Type: Python Project for Learning

## Current Status Snapshot

- Core chess engine rules are implemented (including castling, en passant, promotion, draw rules, and undo).
- SAN-lite notation export/import is implemented and tested.
- Replay controls API (`replay_start`, `replay_next`, `replay_previous`, `replay_end`) is the current in-progress feature.
- Current test status: `88 passed, 5 failed`.
- The 5 failing tests are intentional TDD tests for the replay-controls API.

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
├── requirements.txt     # Project dependencies
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```
