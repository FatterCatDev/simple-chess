# Save and Load Feature Spec (SAN-lite)

## Status
- Implemented in controller and GUI.
- Persisted format: JSON wrapper containing SAN-lite move list.
- Current automated coverage: save/load tests are passing.
- Workspace-wide test status currently is `159 passed, 0 failed`.

## 1. Goal
Add a Save button and Load action that use a full SAN-lite move list as the persisted game format.
The saved notation must be sufficient for the app to reconstruct, replay, and resume a game.

## 2. Scope
In scope:
- Save current game as full SAN-lite move list (in move order).
- Load SAN-lite move list from file/content.
- Reconstruct board state by replaying loaded SAN-lite moves.
- Preserve loaded notation as replay history so replay controls continue to work.
- Resume normal play from the loaded final position.

Out of scope (for this feature slice):
- PGN tags/metadata (`Event`, `Date`, `Result`, etc.).
- Engine format changes beyond SAN-lite.
- Network/cloud storage.

## 3. User Stories
- As a player, I can click Save to export all played moves in SAN-lite.
- As a player, I can later load that SAN-lite list and return to the same final board position.
- As a player, after loading, I can use replay controls and then continue playing from the end.

## 4. Functional Requirements
1. Save action exports the complete result of `export_notation()`.
2. Saved data contains every SAN-lite move in chronological order.
3. Load action accepts a SAN-lite list and calls `load_notation(...)` path.
4. On successful load, board state equals replayed final state of that notation.
5. On successful load, replay state is available (start/previous/next/end continue to work).
6. Player can resume play from final replay position.
7. Invalid/empty save input on load must fail gracefully with a user-facing error.

## 5. Data Contract
Preferred persisted shape (JSON):

```json
{
  "format": "san-lite-list",
  "version": 1,
  "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5"]
}
```

Minimum accepted payload for load:
- A list of SAN-lite strings in order.

Notes:
- `moves` must be non-empty for successful load in current engine behavior.
- SAN-lite includes special move markers already supported by engine logic:
  - castling: `O-O`, `O-O-O`
  - captures: `x`
  - promotion: `=Q`, `=R`, `=B`, `=N`
  - en passant suffix: ` e.p.`
  - check/checkmate suffixes: `+`, `#`

## 6. UX Behavior
Save:
- Trigger: Save button/menu action.
- Result: Writes SAN-lite list to chosen file.
- Success feedback: brief in-board fading success message (for example: "Game saved").
- Failure feedback: show reason and do not change game state.
- Empty-game rule: if no moves exist, save is blocked with a clear message (for example: "No moves to save.").

Load:
- Trigger: Load/Open button/menu action.
- Result: Parse file, validate shape, pass notation to controller load flow.
- Success feedback: board refreshes to loaded final position, replay info updates, and a brief in-board fading success message is shown.
- Failure feedback: show reason and keep current game unchanged.

## 7. Resume and Replay Rules
After successful load:
1. Replay controls can navigate through loaded history.
2. If user is not at replay end, move attempts remain blocked (existing replay restriction).
3. When user reaches replay end and makes a legal move, replay state is cleared and normal game continues (existing controller behavior).

## 8. Error Cases
- File not found.
- File unreadable.
- Invalid JSON.
- Missing `moves` field for JSON payloads.
- `moves` is not a list of strings.
- Empty notation list.
- SAN-lite token cannot be replayed/validated.

Expected behavior:
- No partial apply.
- No silent failure.
- Error text exposed through existing status/error channel.

Policy note:
- Empty SAN-lite files/lists are treated as invalid load input for this feature slice.

## 9. Acceptance Criteria
- Save action exports full SAN-lite move list for the current game.
- Save action is blocked when there are zero moves, with a clear user-facing message.
- Loading the saved file reconstructs the same final board position.
- Replay controls work immediately after load.
- User can resume play from loaded final position.
- Invalid loads fail with clear error and no board mutation.

## 10. Test Plan (Markdown Checklist)
- [x] Save from new game with no moves is blocked with the agreed message.
- [x] Save mid-game creates persisted SAN-lite list with correct move count/order.
- [x] Load valid SAN-lite list reproduces expected final position.
- [x] Load with castling notation reproduces correct king/rook positions.
- [x] Load with en passant notation reproduces correct capture state.
- [x] Load with check/checkmate suffixes parses successfully.
- [x] Replay start/next/previous/end work after load.
- [x] Attempt move mid-replay remains blocked.
- [x] Move at replay end resumes normal play and clears replay state.
- [x] Invalid payload (non-list moves) returns clear error.
- [x] Empty moves list returns clear error.
- [x] Missing `moves` field returns clear error.
- [x] Invalid JSON returns clear error.
- [x] Missing file returns clear error.
- [x] Failed load does not mutate the current board.

Current note:
- Save while replaying uses full replay notation (`replay_notation`) so files are not truncated mid-replay.

## 11. Implementation Notes
- Reuse existing engine/controller APIs:
  - `Game.export_notation()`
  - `Game.load_notation(...)`
  - controller replay restrictions already in place
- Keep Save/Load as thin I/O wrappers around these APIs.
- Treat SAN-lite list as source of truth for reconstruction.

## 12. Definition of Done
- Save/Load feature behavior matches all acceptance criteria.
- Manual verification checklist completed.
- Automated tests for happy path and failure cases are added and passing.
