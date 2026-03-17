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
   - AI engine selection (Random AI, Simple Heuristic Easy/Hard, Stockfish UCI)
   - Player color selection for PvAI (White/Black)
- Board orientation flips when PvAI player color is Black.
- Previous-move highlighting is implemented (`from` and `to` squares).
- Current automated test status: `160 passed, 0 failed`.

## Project Structure

```
Simple Chess/
├── src/
│   ├── ai/
│   ├── game/
│   ├── gui/
│   ├── scripts/
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
python -m unittest discover -s src/tests -t src
```

Current result in this workspace:
- `160 passed, 0 failed`

## Release Notes (2026-03-15)

### AI Stability + Performance

- Refactored Hard `SimpleHeuristicAI` search to use simulation state APIs instead of mutating live game state with repeated `make_move` / `undo_move` cycles.
- Added state simulation modules:
   - `src/ai/sim_state.py`
   - `src/ai/sim_adapter.py`
- Implemented direct state-based legal move generation and state move application for Hard AI lookahead.
- Added bounded transposition caching in Hard AI to reduce repeated state evaluation work.
- Added capped candidate/reply move windows in Hard AI to stabilize per-turn compute cost.

### GUI Autoplay Reliability

- Added non-overlapping auto-play guard in `src/gui/app.py` so AI ticks cannot re-enter while already running.
- Kept fast AI-vs-AI scheduling (`interval = 1ms`) while improving loop safety.
- Added optional top-bar AI debug toggle and throughput label for live tick-rate visibility.

### Test Coverage

- Added regression tests ensuring Hard AI move selection does not mutate live game state.
- Added repeated-turn Hard AI stability test.
- Added legal-move parity tests comparing state engine vs live engine across:
   - start position,
   - developed opening positions,
   - en passant windows,
   - castling available / castling rights removed scenarios.
- Current automated suite result: `160 passed, 0 failed`.

### Running AI Stress Repro Script (Manual)

This is a manual crash-reproduction/stress script (not part of unit test discovery):

```bash
# PowerShell (Windows)
$env:PYTHONPATH="src"
python -m scripts.repro_ai_difficulty2_crash
```

```bash
# macOS/Linux
PYTHONPATH=src python -m scripts.repro_ai_difficulty2_crash
```

## Development

This is a learning project. Feel free to experiment and expand the codebase.

## GitHub Releases (Windows/macOS/Linux)

This repo includes an automated workflow at [.github/workflows/release.yml](.github/workflows/release.yml) that:
- builds on Windows, macOS, and Linux,
- runs tests,
- packages release artifacts,
- uploads artifacts to the run,
- and publishes files to a GitHub Release when you push a version tag.

Current release artifact types:
- Windows: `SimpleChess-windows-x64-installer.exe` (Inno Setup installer)
- macOS: `SimpleChess-macos-x64.dmg`
- Linux: `SimpleChess-linux-x64.AppImage`

### Running release artifacts

- macOS: open `SimpleChess-macos-x64.dmg`, then copy/open `SimpleChess.app`.
- macOS release ships as a `.dmg` image containing `SimpleChess.app`.
- Linux: downloaded AppImage files are not executable by default. You must mark it executable before it will run (otherwise Ubuntu will try to mount it as a disk image).

#### Linux — CLI

```bash
chmod +x SimpleChess-linux-x64.AppImage
./SimpleChess-linux-x64.AppImage
```

#### Linux — GUI (Files / Nautilus)

1. Right-click `SimpleChess-linux-x64.AppImage`
2. Select **Properties**
3. Open the **Permissions** tab
4. Check **Allow executing file as program**
5. Close Properties, then double-click the file to launch it

### PyInstaller dependency behavior

- Python dependencies from `requirements.txt` are installed on the build machine before packaging.
- The generated executable already contains those Python dependencies.
- The executable does not run `pip install` when a user opens it.

### Local executable build

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --clean SimpleChess.spec
```

### Create a release

1. Commit and push your latest code to `main`.
2. Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. Open GitHub → **Releases** to find the generated release with attached artifacts.

### Notes

- The workflow also supports manual start via **Actions → Build and Release → Run workflow**.
- Windows signing is optional: set `WIN_CERT_PFX_BASE64` and `WIN_CERT_PASSWORD` secrets to sign both the app and installer.
- macOS binaries may need signing/notarization for smooth distribution outside your machine.
- Windows binaries may show SmartScreen warnings until reputation/signing is established.

## Rules Notes

- Threefold repetition uses a simplified rule in this project.
- A repeated position is detected from board piece placement snapshots.
- Castling rights and en passant rights are intentionally not included in repetition matching.
- SAN format is SAN-lite and includes custom draw/en passant suffix handling used internally by this project.

## Third-Party Component: Stockfish

- This project includes Stockfish binaries for AI opponent mode.
- Stockfish is licensed under GPL-3.0.
- Included engine files are located under:
   - `src/ai/stockfish/windows/avx2/`
   - `src/ai/stockfish/windows/non-avx2/`
   - `src/ai/stockfish/macos/avx2/`
   - `src/ai/stockfish/macos/non-avx2/`
   - `src/ai/stockfish/ubuntu/avx2/`
   - `src/ai/stockfish/ubuntu/non-avx2/`
- Included license/source bundle is located under:
   - `src/ai/stockfish/shared/`

## Known Issues

- See `design_docs/KNOWN_BUGS.md` for tracked issues and status.

## License

This project is for educational purposes.
