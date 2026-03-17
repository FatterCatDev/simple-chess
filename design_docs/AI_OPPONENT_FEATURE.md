# AI Opponent Feature — Design Document

Last verified: 2026-03-16

## 1. Overview

This feature adds AI-powered opponents to Simple Chess. The current implementation supports built-in engines and Stockfish through a UCI wrapper, with setup available at startup/new-game.

---

## 2. Requirements

### 2.1 Core Requirements
- [x] Player can select an AI opponent before starting a game
- [x] Multiple built-in AI engines/models available (Random, Simple Heuristic)
- [x] Basic difficulty options available for Simple Heuristic (Easy/Hard in UI)
- [ ] Optional LLM Opponent mode available
- [ ] LLM Opponent uses the user's own account (OpenAI or GitHub) for model access
- [x] Game modes: Player vs AI, AI vs AI
- [x] AI makes legal moves respecting all chess rules
- [x] Game ends correctly after AI move (e.g., if AI move leads to checkmate)
- [x] Replay controls work with games played against AI
- [x] Save/load preserves the AI selection and difficulty for context
- [x] UI flow to select game mode, AI engine, and player color before play

### 2.2 Out of Scope (Future)
- Timed games / time controls per side
- OpenBook or endgame tables
- Elo rating display or match scoring
- Online multiplayer

---

## 3. AI Engines and Models

### 3.1 Supported Engines

Engines are organized into three categories:

#### Built-in Engines (Always Available, Phase 1+)
| Engine | Type | Difficulty Levels | Notes |
|---|---|---|---|
| **Random** | Dumb AI | 1 (max variation) | Picks legal moves at random; no evaluation |
| **Simple Heuristic** | Light AI | 2 levels in GUI (Easy/Hard) | Prioritizes material and tactical outcomes using lightweight lookahead |

#### UCI Engines (Installed Locally, Phase 1–3)
| Engine | Rating | Size | Phase | Notes |
|---|---|---|---|---|
| **Stockfish** | ~3500 ELO | ~10 MB | 1 (MVP) | Industry standard; free; easiest to integrate |
| **Leela Chess Zero** | ~3200 ELO | ~100 MB | 3 | Neural network; different play style |
| **Komodo** | ~3300 ELO | ~7 MB | 3 | Commercial engine; free download |
| **Arasan** | ~2900 ELO | ~5 MB | 3 | Open source; lightweight |

**Current Scope:** Built-in engines (Random, Simple Heuristic) + Stockfish via UCI

**Phase 3 Scope:** Add multi-engine support via generic UCI wrapper; player can choose Stockfish, Leela, or other UCI engines

### 3.2 Engine Initialization
Each engine is wrapped in a unified interface (see Section 5). At game setup, the chosen engine is instantiated with:
- Difficulty level (affects search depth, time budget, or eval heuristics)
- UCI binary path (for UCI engines; `None` for built-in engines)
- (Optional) Opening book preference or other UCI options

#### Difficulty Layout (Current Design)
- `Random AI`: fixed at difficulty `1` (no slider range).
- `Simple Heuristic AI`: slider range `1–2`.
    - `1` = greedy mode
    - `2` = lookahead mode
- `Stockfish (UCI)`: slider range `1–10` (user-facing scale).
    - Skill Level mapping contract: `1 -> 0`, `10 -> 20`.
    - Skill Level formula: `round((difficulty - 1) * 20 / 9)` with difficulty clamped to `1..10`.
    - Runtime precedence rule: if `move_time_ms` is not configured, engine uses fixed `go depth 12`.
    - If `move_time_ms` is configured, engine uses `go movetime ...` and depth is not sent.

### 3.3 LLM Models (Cloud, User-Owned Access)

LLM Opponent is treated as a separate model family from UCI engines.

| Provider | Access | Account Owner | Notes |
|---|---|---|---|
| **OpenAI** | API key / OAuth token | End user | User supplies their own credentials in-app |
| **GitHub Models** | GitHub login/token | End user | User signs in with their GitHub account |

Design rule: the app must not rely on a developer-owned shared key for LLM Opponent mode.
Each user authorizes their own account and quota.

---

## 4. Game Modes

### 4.1 Player vs AI
- Human player selects color (White or Black)
- AI opponent plays the opposite color
- After player move, UI waits for AI to compute and play
- Board updates reflect AI move
- Game continues until checkmate, stalemate, or draw rule
- If the player selects Black, AI (White) makes the first move automatically after setup

### 4.2 AI vs AI
- Two AI engines (may be same model at different difficulties or different models)
- Current behavior: continuous autonomous loop is implemented through auto-play scheduling while AI still has turns
- Player can watch or step through using replay controls
- Game runs at a configurable pace (instant, 1 sec per move, etc.)

### 4.3 Player vs Player (Existing)
- No AI involved; existing hotpath behavior

---

## 5. Architecture

### 5.1 AI Engine Interface

Define a common interface (abstract base or protocol) that all engines implement:

```python
class AIEngine:
    """Abstract base for chess AI engines."""
    
    def get_move(self, game: Game) -> tuple | None:
        """
        Analyze the position and return a move.
        
        Args:
            game: Current Game object
        
        Returns:
            (from_square, to_square) tuple, or None if no moves available
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
```

**Note:** The current implementation uses `get_move(game)` returning either `(from_sq, to_sq)` or `(from_sq, to_sq, promotion_choice)` for promotion-aware paths.

### 5.2 Engine Implementations

#### 5.2.1 UCI Engine Wrapper (Generic, Phase 1+)

A generic `UCIEngine` class that communicates with any UCI-compliant binary:

```python
class UCIEngine(AIEngine):
    """Wrapper for any UCI-compliant chess engine (Stockfish, Leela, etc.)."""
    
    def __init__(self, name: str, binary_path: str):
        self.name = name
        self.binary_path = binary_path
        # Engine process spawned on first get_move() call
    
    def get_move(self, game: Game) -> tuple | None:
        """Send position to UCI engine; return a legal move tuple."""
        # If movetime is configured, use go movetime.
        # Otherwise use a fixed fallback depth.
        depth = 12
        # Spawn engine subprocess, send UCI commands, collect bestmove
        return (from_sq, to_sq)
```

    **Difficulty Mapping (UI Layout):**
    - Random: fixed 1
    - Heuristic: 1–2
    - Stockfish (UI): 1–10
    - Stockfish search depth stays fixed at `12` when `move_time_ms` is not set (slider does not change depth)

    **Stockfish Command Priority:**
    0. Set engine skill using `setoption name Skill Level value <mapped_skill>` from UI difficulty `1..10`.
    1. If `move_time_ms` is set, send `go movetime <ms>`.
    2. Else send `go depth 12`.

**Phase 1 MVP:** Instantiate for Stockfish only

**Phase 3 Multi-Engine:** Reuse same wrapper for Leela, Komodo, etc.

#### 5.2.2 Stockfish (Phase 1+)
- Instantiate as `UCIEngine("Stockfish", path_to_binary)`
- Requires Stockfish binary pre-installed; path set in config or environment
- Uses UCI protocol to communicate
- Uses UI difficulty scale 1–10 for setup/save metadata
- Uses UI difficulty scale 1–10 mapped to Stockfish `Skill Level` 0–20
- Uses fixed `go depth 12` when `move_time_ms` is not configured

#### 5.2.3 Leela Chess Zero (Phase 3+)
- Instantiate as `UCIEngine("Leela Chess Zero", path_to_lc0_binary)`
- Same UCI wrapper; different binary and play style (neural network)
- Difficulty scaling same as Stockfish

#### 5.2.4 Random
- Iterates over all squares, collects legal `(from_sq, to_sq)` pairs from `game.get_legal_moves(square)`, picks one at random
- Difficulty level ignored
- Useful for testing and baseline
- **Status: Implemented** (`src/ai/ai.py`)

#### 5.2.5 Simple Heuristic
- Evaluates all legal moves using hand-crafted scoring (captures > checks > piece safety > mobility)
- Difficulty levels currently implemented: 1=greedy and 2=lookahead
- Fast, no engine binary required
- **Status: Implemented** (`src/ai/simple_heuristic_ai.py`)

#### 5.2.6 LLM Opponent (Cloud, User Account)
- Uses model access from the user's authenticated OpenAI or GitHub account
- Must receive board state every turn to minimize hallucinations
- Must be constrained to pick exactly one move from legal moves provided by the engine

Per-turn payload (token-efficient):
- `FEN`
- Side to move
- Legal SAN moves list
- Difficulty/style profile (e.g., casual, tactical, aggressive)

Per-turn response contract:
- Return exactly one SAN move from provided legal moves
- No additional text in strict mode

Validation and fallback:
- If response is invalid, timed out, or not in legal list, fallback to a legal move strategy (Random or Stockfish)
- Log fallback reason for transparency

### 5.3 Game Controller Extension

Extend `GameController` with AI support:

```python
class GameController:
    def __init__(self, game: Game, ai_white: AIEngine | None = None, ai_black: AIEngine | None = None):
        ...
        self.ai_white = ai_white
        self.ai_black = ai_black
        self.ai_difficulty_white = 5  # Default
        self.ai_difficulty_black = 5  # Default
    
    def try_move(self, to_position, promotion_choice="Q") -> bool:
        """Existing method; no changes."""
        ...
    
    def should_ai_move(self) -> bool:
        """Return True if the current player is controlled by AI."""
        current_ai = self.ai_white if self.game.current_turn == "W" else self.ai_black
        return current_ai is not None
    
    def get_ai_move(self) -> tuple | None:
        """Get the next move from the AI."""
        current_ai = self.ai_white if self.game.current_turn == "W" else self.ai_black
        return current_ai.get_move(self.game)
    
    def make_ai_move(self) -> bool:
        """Execute the AI's chosen move."""
        if not self.should_ai_move():
            return False
        move_san = self.get_ai_move()
        # Convert SAN to from/to squares and call try_move
        ...
```

### 5.4 GUI Integration

Add a new screen or dialog **before** the main game board:

**Setup Dialog Flow:**
1. User clicks "New Game"
2. Dialog opens: "Game Setup"
   - Radio buttons: "Player vs AI" / "AI vs AI" / "Player vs Player"
   - If "Player vs AI":
     - Dropdown: White or Black (player color)
     - Dropdown: AI engine (Stockfish, Random, Simple Heuristic, etc.)
         - Slider/spinner: Difficulty (engine-dependent range)
             - Random: fixed at 1
             - Heuristic: 1–2
             - Stockfish: 1–10
   - If "AI vs AI":
     - Dropdown (Engine 1): Stockfish, Random, etc.
         - Slider (Difficulty 1): engine-dependent range
     - Dropdown (Engine 2): Stockfish, Random, etc.
         - Slider (Difficulty 2): engine-dependent range
   - If "Player vs Player":
     - Checkbox (optional): "Auto-play against CPU" (disables for now, reserved for future)
3. Click "Start Game" → Initialize `GameController` with chosen engines and close dialog

**Game Board Changes:**
- Add a status indicator showing whose turn it is and if it's an AI.
- If AI move is being computed, show a loading spinner or message ("AI thinking...").
- Auto-advance the board after AI move (no click needed).

### 5.5 Save/Load Behavior

When saving a game with AI:
```json
{
  "format": "san-lite-list-with-ai",
  "version": 2,
  "moves": ["e4", "e5", ...],
  "game_mode": "Player vs AI",
  "ai_white": {
    "engine": "Stockfish",
    "difficulty": 10
  },
  "ai_black": null
}
```

When loading, reconstruct the same `GameController` with the stored AI settings.

### 5.6 Authentication and Credential Ownership

LLM Opponent authentication requirements:
- User can connect either OpenAI account or GitHub account
- Credentials/tokens are user-owned and tied to their account
- App stores credentials securely (OS credential vault preferred); never commit to repo
- App provides explicit sign-out/disconnect action

Credential policy:
- No hardcoded API keys
- No project-wide shared paid key required for gameplay
- If user is not authenticated, LLM Opponent options are disabled with clear UI message

Privacy policy (design-level):
- Only send minimum turn context needed for move selection
- Do not send local file paths or unrelated user data to model providers

### 5.7 Dedicated AI Simulation State (No Live Undo Loop)

Goal: harden AI decision-making by removing repeated `make_move`/`undo_move` calls against the live `Game` object during search.

#### Design Decision
- Keep `Game` as the authoritative runtime state for UI/controller/replay.
- Introduce an AI-only lightweight state model used exclusively inside engine search.
- AI search becomes pure simulation (`apply_move -> next_state`) instead of mutating and undoing live game state.

#### AI Simulation Components
- `AIState`: immutable snapshot containing `pieces`, `current_turn`, `last_move`, `halfmove_clock`, draw/check flags, and serialized `position_history`.
- `PieceState`: immutable piece record (`position`, `color`, `piece_type`, `has_moved`).
- `LastMoveState`: immutable last-move record used for en passant and move context.
- `generate_legal_moves(state)`: pure function for legal move generation from `AIState`.
- `apply_move_on_state(state, from_square, to_square, promotion_choice="Q") -> AIState`: returns a derived state for search expansion.
- `evaluate_state(state)`: static evaluation function used by heuristic search.

#### Integration Boundary
- Before AI turn: convert current `Game` into `AIState`.
- AI computes best move using simulation-only search.
- After decision: apply exactly one final move to live `Game` through normal controller/game API.
- Replay, SAN-lite export/import, save/load, and UI updates remain tied to live `Game` only.

#### Why This Change
- Eliminates state-corruption risk from incomplete undo paths during exceptions.
- Reduces coupling between AI internals and UI/game lifecycle.
- Improves reliability in AI-vs-AI and rapid autoplay scenarios.

#### Rollout Plan (Incremental)
1. Add `AIState` + converter layer (`Game -> AIState`).
2. Implement simulation move generation and `apply_move` for current built-in engine needs.
3. Switch `SimpleHeuristicAI` Hard mode search to simulation path.
4. Keep Easy mode unchanged initially; migrate later if desired.
5. Add stress tests for long AI-vs-AI runs to confirm no crash/regression.

#### Non-Goals (MVP)
- Full SAN-based simulation for search.
- Replacing existing replay pipeline.
- Introducing transposition tables/opening books in first pass.

---

## 6. UI / UX Flow

### 6.1 Main Menu (Future Enhancement)

When app launches, show:
- "New Game" → Pops the Setup Dialog
- "Load Game" → Existing behavior
- "Continue" → Resume last game (if game was in progress)

### 6.2 Setup Dialog

```
┌─────────────────────────────────────────┐
│         Game Setup                      │
├─────────────────────────────────────────┤
│                                         │
│  Game Mode:                             │
│  ○ Player vs Player                     │
│  ○ Player vs AI                         │
│  ○ AI vs AI                             │
│                                         │
│  [If Player vs AI selected:]            │
│    Your Color: ○ White ● Black          │
│    AI Engine: ┌─────────────────────┐   │
│               │ Stockfish           │   │
│               │ Random              │   │
│               │ Simple Heuristic    │   │
│               │ LLM Opponent        │   │
│               └─────────────────────┘   │
│    Difficulty: ░░░░░░░░░░░░░░░░░░░░ 10 │
│    Provider: OpenAI / GitHub            │
│    [ Sign in ]  [ Disconnect ]          │
│                                         │
│  [ Start ]  [ Cancel ]                  │
└─────────────────────────────────────────┘
```

### 6.3 In-Game Status

Status bar at top shows:
- Whose turn: "White's turn" → "AI thinking..." (if AI) → "Black's move"
- Move counter: "Move 15"
- Game mode: "Player (Black) vs AI (Stockfish, Hard)"
- LLM auth status when selected: "LLM: Connected (OpenAI)" or "LLM: Not connected"

---

## 7. Implementation Roadmap

### Phase 1: Foundations (MVP)
**Goal:** Built-in engines + Stockfish via UCI wrapper; GameController wiring; core tests

#### Phase 1A: AI Simulation Engine Track (Crash-Prevention Priority)
**Goal:** Move Hard heuristic search off live `Game` mutation and onto AI-only simulation state.

- [x] Add `src/ai/sim_state.py`
    - Define immutable `AIState`, `PieceState`, and `LastMoveState`
- [x] Add `src/ai/sim_adapter.py`
    - `game_to_ai_state(game) -> AIState`
- [x] Add state legal-move and apply-move functions in `src/ai/sim_adapter.py`
    - `generate_legal_moves(state)`
    - `apply_move_on_state(state, from_square, to_square, promotion_choice="Q") -> AIState`
    - Keep implementation minimal and focused on current built-in engine requirements
- [x] Update `src/ai/simple_heuristic_ai.py`
    - Hard mode uses simulation path only
    - Easy mode can remain current path in first pass
    - Remove reliance on live `make_move/undo_move` within Hard search
- [x] Add tests in `src/tests/test_ai_engines.py`
    - Hard mode returns legal move in tactical positions
    - Hard mode no longer mutates live game during search
    - Regression test for previous crash reproduction pattern
- [ ] Add optional stress test script update in `src/scripts/repro_ai_difficulty2_crash.py`
    - Increase iterations and assert no exception/state corruption

**Definition of Done (Phase 1A):**
- [x] No Hard AI search path uses live `Game.undo_move()`
- [x] Existing unit tests still pass
- [ ] Hard AI completes long autoplay runs without crash in repro script
- [x] Move quality remains at least equal to current Hard baseline on tactical tests

#### Phase 1A API Contract (Implemented)

`src/ai/sim_state.py`
```python
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class PieceState:
    position: str
    color: str
    piece_type: str
    has_moved: bool

@dataclass(frozen=True)
class LastMoveState:
    from_square: str
    to_square: str
    was_two_square_pawn_move: bool

@dataclass(frozen=True)
class AIState:
    pieces: Tuple[PieceState, ...]
    current_turn: str
    game_over: bool
    is_draw: bool
    draw_reason: Optional[str]
    halfmove_clock: int
    is_in_check: bool
    last_move: Optional[LastMoveState]
    position_history: Tuple[Tuple[Tuple[str, Optional[Tuple[str, str]]], ...], ...]
    enable_fifty_move_rule: bool
```

`src/ai/sim_adapter.py`
```python
from ai.sim_state import AIState

def game_to_ai_state(game) -> AIState:
    """Convert live Game into immutable AIState snapshot."""

def generate_legal_moves_on_state(state) -> list[tuple[str, str]]:
    """Return all legal (from_square, to_square) moves for state.current_turn."""

def apply_move_on_state(state, from_square, to_square, promotion_choice="Q") -> AIState:
    """Return next immutable AIState after the given move."""

def is_in_check_state(state, color) -> bool:
    """True if color king is currently in check in state."""
```

`src/ai/simple_heuristic_ai.py` integration target
```python
def _best_lookahead_move(self, game, moves):
    state = game_to_ai_state(game)
    candidate_moves = generate_legal_moves_on_state(state)
    # Evaluate using apply_move_on_state(state, from_square, to_square), never mutating live game.
    # Return (from_sq, to_sq) compatible with existing controller path.
```

Implementation rule for Phase 1A:
- Hard mode (`difficulty >= 2`) must use only `AIState` simulation functions.
- No live `game.make_move(...)` and no live `game.undo_move()` inside Hard search path.
- Final selected move is applied once by existing live game flow.

#### Engines
- [x] Design and implement `AIEngine` base interface (`src/ai/ai.py`)
- [x] Implement `RandomAI` engine (built-in) (`src/ai/ai.py`)
- [x] Implement `SimpleHeuristicAI` engine (built-in; hand-crafted evaluation) (`src/ai/simple_heuristic_ai.py`)
- [x] Implement `UCIEngine` wrapper (generic UCI binary support for Stockfish, Leela, etc.)

#### Controller
- [x] Extend `GameController` with `ai_white` / `ai_black` fields
- [x] Add `should_ai_move()` and `make_ai_move()` methods
- [x] Support passing engine instances to `GameController.__init__()`

#### Testing
- [x] Add unit tests for `RandomAI` (`TestGameControllerAIMode` in `src/tests/test_controller.py`)
- [x] Add unit tests for `SimpleHeuristicAI` (`src/tests/test_ai_engines.py`)
- [x] Add unit tests for `UCIEngine` move parsing/response behavior
- [ ] Add integration tests: `GameController` with Random vs Random
- [x] Add `GameController` handling for 2-tuple and 3-tuple AI moves (promotion-aware)
- [ ] Test that all AI moves are legal in all positions

#### Configuration
- [x] Document bundled Stockfish binary layout (Windows/macOS/Linux paths)
- [x] Resolve Stockfish binary paths via `src/gui/ai_mode.py` with platform-aware candidates and fallback
- [x] Add graceful fallback if Stockfish binary unavailable (fallback to RandomAI)

### Phase 2: UI
**Goal:** Setup dialog; auto-play loop; end-to-end playable

- [x] Wire `RandomAI` as Black in `app.py`; AI auto-replies after each human move
- [x] Player name labels above/below board reflect active game mode (e.g., "AI (Black)" / "Player 1")
- [x] Create Setup Dialog (`show_mode_dialog()`): Tkinter Toplevel with radio buttons (PvP, PvAI, AIvAI) and Start/Cancel buttons
- [x] Wire "New Game" and app startup to show Setup Dialog
- [x] Wire Start → initialize `GameController` via centralized mode builder
- [x] Add engine selection dropdown to Setup Dialog (Random + Simple Heuristic + Stockfish)
- [ ] Add engine-dependent difficulty slider to Setup Dialog
    - Random fixed at 1
    - Heuristic range 1–2
    - Stockfish range 1–10
- [x] Add auto-play loop for AI vs AI mode
- [ ] Update status label to show "AI thinking..." during move computation
- [x] Handle game-over during AI move (dialog triggers via refresh flow)
- [ ] Manual testing: Player vs Stockfish, Random vs Random, Heuristic vs Stockfish

---

## 8. Current Reality Snapshot

- Implemented now: mode dialog + engine selection + player color selection + flipped board for Black player in PvAI.
- Implemented now: first AI move triggers automatically when AI controls White at game start.
- Implemented now: dedicated AI-vs-AI continuous autoplay loop with non-overlapping scheduling guard.
- Implemented now: Stockfish UCI integration with platform-aware path resolution, primary/secondary binary fallback, and runtime error handling.
- Not implemented yet: LLM opponent mode.

### Phase 3: Multi-Engine Expansion
**Goal:** Add Leela and other UCI engines; player can choose at setup

- [ ] Download/configure Leela Chess Zero binary (or other UCI engines)
- [ ] Verify `UCIEngine` wrapper works with multiple engines
- [ ] Update Setup Dialog engine dropdown to list all available UCI engines
- [ ] Auto-detect installed engines at startup (check common system paths)
- [ ] Update README with multi-engine setup instructions
- [ ] Test Leela vs Stockfish, Leela vs Random, etc.

### Phase 4: LLM Opponent Mode
**Goal:** Add cloud LLM play using user-owned account credentials

- [ ] Implement `LLMEngine` adapter with strict move-output schema
- [ ] Add provider selection (OpenAI, GitHub) in setup dialog
- [ ] Implement sign-in/sign-out flows and secure token storage
- [ ] Build token-efficient per-turn prompt protocol (`FEN` + legal SAN list)
- [ ] Add invalid-response fallback to Random/Stockfish
- [ ] Add model timeout and retry policy
- [ ] Add UI status indicators: connected/disconnected, provider, fallback events

### Phase 5: Enhancements (Post-MVP)
- [ ] Extend AI context schema beyond current v2 save/load format (optional metadata)
- [ ] Main menu with "Continue Game" option
- [ ] AI vs AI auto-play speed control (slider: instant, 1 sec/move, 2 sec/move)
- [ ] ELO display or performance metrics (optional)
- [ ] UCI engine advanced options (hash, threads, opening books)

---

## 9. Test Plan

### 8.1 Unit Tests: AI Engines

| Scenario | Test |
|---|---|
| Random engine picks legal move | Play Random on various positions; assert move is in legal moves |
| Random engine raises on stalemate | Call Random with game_over=True; expect ValueError |
| SimpleHeuristic prioritizes capture | Position with 2 legal moves (capture or quiet); assert capture chosen |
| SimpleHeuristic handles checkmate move | Position where only move is checkmate; assert that move chosen |
| Stockfish skill mapping | Verify setup maps difficulty 1 to `Skill Level 0` and difficulty 10 to `Skill Level 20` |
| Stockfish fallback depth policy | With `move_time_ms` unset, verify `go depth 12` command path is used |
| LLM move is validated | Mock LLM response not in legal list; assert fallback strategy used |
| LLM timeout fallback | Mock timeout; assert engine selects fallback legal move |

### 8.2 Integration Tests: GameController + AI

| Scenario | Test |
|---|---|
| Player vs RandomAI completes game | Initialize controller; play until checkmate; assert game_over=True |
| RandomAI vs RandomAI completes | Play both sides with Random; verify game terminates |
| Load game with AI preserves choices | Save game with StockfishAI, load back; assert engine name matches |
| AI move respects all rules | Play AI in position with castling/en passant available; verify legality |
| LLM auth required | Select LLM without login; assert game start blocked with clear message |
| LLM provider flow | Sign in via OpenAI/GitHub mock and start game; assert engine becomes available |

### 8.3 GUI Tests (Manual / E2E)

| Test | Steps | Expected |
|---|---|---|
| Setup Dialog opens | Click "New Game" | Dialog appears with game mode options |
| Select "Player vs AI" | Radio button selection | AI engine dropdown and engine-dependent difficulty slider show |
| Start game with AI | Choose engine, difficulty, click Start | Board appears; AI plays first move after user move |
| Status updates | Play move as Player | Status shows "White's move" → "AI thinking..." → "Black's move" |
| Save game with AI | Play a few moves | Save dialog; JSON contains selected `"engine"` and selected `"difficulty"` |

---

## 10. Files to Create/Modify

| File | Change | Phase | Status |
|---|---|---|---|
| `src/ai/ai.py` | New: Base `AIEngine` class + `RandomAI` implementation (consolidated) | 1 | Done |
| `src/ai/simple_heuristic_ai.py` | New: `SimpleHeuristicAI` implementation | 1 | Done |
| `src/ai/sim_state.py` | New: immutable AI simulation state models | 1A | Done |
| `src/ai/sim_adapter.py` | New: state adapters, legal moves, and state move application | 1A | Done |
| `src/ai/uci_engine.py` | New: Generic `UCIEngine` wrapper for Stockfish, Leela, etc. | 1 | Done |
| `src/ai/config.py` | New: Engine paths and configuration | 1 | Pending |
| `src/ai/__init__.py` | Export engine classes | 1 | Pending |
| `src/gui/controller.py` | Update `GameController.__init__()` and add `should_ai_move()`, `make_ai_move()` | 1 | Done |
| `src/gui/app.py` | Setup dialog + AI autoplay loop + non-overlapping guard + debug throughput toggle + AI shutdown lifecycle hooks | 2 | Partial |
| `src/tests/test_ai_engines.py` | New: Unit tests for RandomAI, SimpleHeuristic, UCIEngine | 1 |
| `src/tests/test_controller_ai.py` | New: Integration tests for GameController + AI | 1 |
| `requirements.txt` | Add chess library and/or python-chess (Phase 1+) | 1 |
| `README.md` | Add AI setup instructions; multi-engine doc (Phase 3) | 1, 3 |
| `src/ai/llm_engine.py` | New: `LLMEngine` adapter with strict move contract and fallback hooks | 4 |
| `src/ai/auth.py` | New: Provider login/token management for OpenAI/GitHub | 4 |
| `src/tests/test_llm_engine.py` | New: LLM response validation, timeout, and fallback tests | 4 |
| `src/tests/test_auth_flow.py` | New: Login/logout and provider availability tests | 4 |
| `README.md` | Add LLM account setup (OpenAI/GitHub) and privacy notes | 4 |
| `design_docs/AI_OPPONENT_FEATURE.md` | This file | All |

---

## 11. Acceptance Criteria

- [ ] Player can start a Player vs AI game
- [ ] Player can start an AI vs AI game
- [ ] AI engine picks a legal move in every position
- [ ] Easy AI (difficulty 1) vs Easy AI completes a full game
- [ ] Stockfish difficulty mapping is correct (`1 -> Skill Level 0`, `10 -> Skill Level 20`)
- [ ] Stockfish fallback depth behavior is correct (`go depth 12` when no movetime)
- [ ] User can sign in with OpenAI or GitHub to enable LLM Opponent
- [ ] LLM Opponent is disabled when user is not authenticated
- [ ] LLM move selection always resolves to a legal move (direct or fallback)
- [ ] Game-over dialog appears correctly after AI delivers checkmate
- [ ] Save game captures AI engine type and difficulty
- [ ] Load game with AI restores the setup correctly
- [ ] Status label shows "AI thinking..." during AI move computation
- [ ] All tests pass: unit tests for engines + integration tests for controller
- [ ] No regressions: existing Player vs Player mode still works

---

## 12. Questions & Decisions

1. **Should AI move be instant or have artificial delay?**
   - *Proposed:* Instant for now; add optional delay slider in Phase 4

2. **How to handle Stockfish binary availability?**
   - *Proposed:* Graceful fallback: if binary unavailable, offer SimpleHeuristic + Random only; log warning to status

3. **What happens if player tries to undo an AI move?**
   - *Proposed:* Undo is blocked during AI's turn; after AI move, undo works normally (same as Player vs Player)

4. **Should saved games include enough data to replay positions exactly?**
   - *Proposed:* Yes; save full SAN list; replay works identically whether opponent was human or AI

5. **Can player switch difficulty mid-game?**
   - *Proposed:* Not for MVP; future feature

6. **How much context should be sent to the LLM each turn?**
    - *Proposed:* Send only `FEN`, side-to-move, legal SAN list, and style profile. Do not send full move history by default.

7. **Who pays for and controls LLM usage?**
    - *Proposed:* End user via their own OpenAI or GitHub account. No developer-shared key.

