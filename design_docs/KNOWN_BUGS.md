# Simple Chess — Known Bugs

This file tracks currently open issues and recently fixed bugs.

---

## Current Test Baseline

- Automated test status: 160 passed, 0 failed

---

## Open Bugs

### BUG-002: Replay move number label not shown as dedicated UI element

- Area: gui
- Severity: Low
- Status: Open
- Reported: 2026-03-13

Description:
Replay mode highlights the current move in history, but there is no separate move counter label like "Move 14 / 40".

Notes:
Functionally replay works; this is a UX enhancement gap.

### BUG-004: No in-app Rules/Help dialog

- Area: gui
- Severity: Low
- Status: Open
- Reported: 2026-03-13

Description:
There is no dedicated Help/Rules dialog in the current UI.

Notes:
Tracked as a future UX improvement.

---

## Fixed Bugs

### BUG-003: No game-over dialog after checkmate or draw

- Area: gui
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-13
- Fixed: 2026-03-14

Summary:
Game-over dialog is implemented and shown for live (non-replay) game-over states.

### BUG-005: Game mode hardcoded at startup/new game

- Area: gui
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-13
- Fixed: 2026-03-14

Summary:
Mode dialog now supports PvP, PvAI, and AIvAI with engine and player-color selection.

### BUG-006: Save during replay produced truncated notation

- Area: controller
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-13
- Fixed: 2026-03-13

Summary:
Saving during replay now uses full replay notation so files are not truncated at current replay index.

### BUG-007: Out-of-bounds squares raised exception instead of returning False

- Area: game/rules
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-14
- Fixed: 2026-03-14

Summary:
Move validation now rejects invalid squares safely, and tests are green.

### BUG-008: Previous-move highlight overwritten during refresh

- Area: gui
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-14
- Fixed: 2026-03-14

Summary:
Board refresh now uses a single highlight priority chain so previous move highlighting persists.

### BUG-009: Move history stored full position-history copy per move (memory growth)

- Area: game
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-14
- Fixed: 2026-03-14

Summary:
Removed redundant position-history copy from each move-history entry to avoid O(N²) memory growth.

### BUG-010: Hard AI crash risk from live-state simulation path

- Area: ai
- Severity: High
- Status: Fixed
- Reported: 2026-03-15
- Fixed: 2026-03-15

Summary:
Hard `SimpleHeuristicAI` lookahead previously relied on repeated live-state mutation patterns that could leave inconsistent state during error paths. The engine now uses immutable AI simulation state and state-based legal move generation for lookahead.

### BUG-011: AI autoplay tick re-entry could overlap moves

- Area: gui
- Severity: Medium
- Status: Fixed
- Reported: 2026-03-15
- Fixed: 2026-03-15

Summary:
Added a non-overlapping autoplay guard so a new AI tick cannot start while one is still running, preventing overlapping turn execution.
