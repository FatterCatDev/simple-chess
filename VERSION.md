# Version Tracker

Current version: **v0.0.9-alpha**

## Release History

### v0.0.9-alpha (2026-03-16)
- Added Stockfish UCI integration with cross-platform binary resolution and fallback behavior.
- Added promotion-aware AI move handling and improved AI error recovery.
- Added AI lifecycle cleanup during mode changes, load, and app close.
- Updated Hard Simple Heuristic AI path to generate root legal moves from simulation state in difficulty 2+.
- Added regression test to ensure Hard AI does not call live `get_all_valid_moves`.
- Updated release workflow packaging for Windows, macOS, and Linux Stockfish assets.
- Updated project documentation to match current implementation and test status.
- Test baseline: `160 passed, 0 failed`.
