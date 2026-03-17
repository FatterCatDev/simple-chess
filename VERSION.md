# Version Tracker

Current version: **v0.0.12-alpha**

## Release History

### v0.0.12-alpha (2026-03-17)
- Added engine-dependent difficulty sliders in setup dialog for PvAI and AIvAI.
- Added dynamic slider range updates based on selected engine (Random 1, Heuristic 1-2, Stockfish 1-10).
- Wired Stockfish UI difficulty (`1..10`) to UCI `Skill Level` (`0..20`) using clamped mapping.
- Added UCI tests for Stockfish skill mapping and option command emission.
- Updated project docs and baseline to `165 passed, 0 failed`.

### v0.0.11-alpha (2026-03-16)
- Fixed Heuristic AI crash when generating root legal moves from simulation state in difficulty 2+.

### v0.0.10-alpha (2026-03-16)
- Minor bugfixes and documentation updates.

### v0.0.9-alpha (2026-03-16)
- Added Stockfish UCI integration with cross-platform binary resolution and fallback behavior.
- Added promotion-aware AI move handling and improved AI error recovery.
- Added AI lifecycle cleanup during mode changes, load, and app close.
- Updated Hard Simple Heuristic AI path to generate root legal moves from simulation state in difficulty 2+.
- Added regression test to ensure Hard AI does not call live `get_all_valid_moves`.
- Updated release workflow packaging for Windows, macOS, and Linux Stockfish assets.
- Updated project documentation to match current implementation and test status.
- Test baseline: `160 passed, 0 failed`.
