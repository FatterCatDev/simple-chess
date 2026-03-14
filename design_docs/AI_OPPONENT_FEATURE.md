# AI Opponent Feature — Design Document

## 1. Overview

This feature adds AI-powered opponents to Simple Chess, allowing players to challenge computer players of varying strengths. The design supports multiple AI engines/models and difficulty levels, enabling rich gameplay scenarios including Player vs AI, AI vs AI, and future extensibility to new engines.

---

## 2. Requirements

### 2.1 Core Requirements
- [ ] Player can select an AI opponent before starting a game
- [ ] Multiple AI engines/models available (e.g., Stockfish, random, simple heuristic)
- [ ] Multiple difficulty levels per engine (e.g., Stockfish ELO 1000, 1600, 2000)
- [ ] Optional LLM Opponent mode available
- [ ] LLM Opponent uses the user's own account (OpenAI or GitHub) for model access
- [ ] Game modes: Player vs AI, AI vs AI
- [ ] AI makes legal moves respecting all chess rules
- [ ] Game ends correctly after AI move (e.g., if AI move leads to checkmate)
- [ ] Replay controls work with games played against AI
- [ ] Save/load preserves the AI selection and difficulty for context
- [ ] UI flow to select game mode, AI engine, and difficulty before play

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
| **Simple Heuristic** | Light AI | 1–3 (basic tactics to simple planning) | Prioritizes captures, checks, and piece safety; no tree search |

#### UCI Engines (Installed Locally, Phase 1–3)
| Engine | Rating | Size | Phase | Notes |
|---|---|---|---|---|
| **Stockfish** | ~3500 ELO | ~10 MB | 1 (MVP) | Industry standard; free; easiest to integrate |
| **Leela Chess Zero** | ~3200 ELO | ~100 MB | 3 | Neural network; different play style |
| **Komodo** | ~3300 ELO | ~7 MB | 3 | Commercial engine; free download |
| **Arasan** | ~2900 ELO | ~5 MB | 3 | Open source; lightweight |

**MVP Scope:** Built-in engines (Random, Simple Heuristic) + Stockfish UCI engine

**Phase 3 Scope:** Add multi-engine support via generic UCI wrapper; player can choose Stockfish, Leela, or other UCI engines

### 3.2 Engine Initialization
Each engine is wrapped in a unified interface (see Section 5). At game setup, the chosen engine is instantiated with:
- Difficulty level (affects search depth, time budget, or eval heuristics)
- UCI binary path (for UCI engines; `None` for built-in engines)
- (Optional) Opening book preference or other UCI options

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

### 4.2 AI vs AI
- Two AI engines (may be same model at different difficulties or different models)
- UI auto-plays both sides
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

**Note:** The current implementation uses `get_move(game)` returning a `(from_sq, to_sq)` tuple rather than SAN notation. When Stockfish/UCI engines are integrated (Phase 1+), the interface may be extended to support difficulty and SAN output as originally planned.

### 5.2 Engine Implementations

#### 5.2.1 UCI Engine Wrapper (Generic, Phase 1+)

A generic `UCIEngine` class that communicates with any UCI-compliant binary:

```python
class UCIEngine(AIEngine):
    """Wrapper for any UCI-compliant chess engine (Stockfish, Leela, etc.)."""
    
    def __init__(self, name: str, binary_path: str):
        self.name = name
        self.binary_path = binary_path
        # Engine process spawned on first get_best_move() call
    
    def get_best_move(self, game_state: Game, difficulty: int) -> str:
        """Send position to UCI engine; return best move at given depth."""
        # Translate difficulty (1-20) to UCI depth
        depth = max(1, min(20, difficulty))
        # Spawn engine subprocess, send UCI commands, collect bestmove
        return best_move_san
```

**Difficulty Mapping:**
- Difficulty 1–3 → depth 1–3 (very fast; <1 sec)
- Difficulty 4–10 → depth 4–10 (intermediate; 1–3 sec)
- Difficulty 11–20 → depth 11–20 (strong; 3–10 sec)

**Phase 1 MVP:** Instantiate for Stockfish only

**Phase 3 Multi-Engine:** Reuse same wrapper for Leela, Komodo, etc.

#### 5.2.2 Stockfish (Phase 1+)
- Instantiate as `UCIEngine("Stockfish", path_to_binary)`
- Requires Stockfish binary pre-installed; path set in config or environment
- Uses UCI protocol to communicate
- Maps difficulty 1–20 to search depth

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
- Difficulty levels: 1=greedy (pick highest immediate score), 2=lookahead 1 move, 3=lookahead 1 move for both sides (minimax-ish)
- Fast, no engine binary required

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
    
    def get_ai_move(self) -> str:
        """Get the next move from the AI."""
        current_ai = self.ai_white if self.game.current_turn == "W" else self.ai_black
        difficulty = self.ai_difficulty_white if self.game.current_turn == "W" else self.ai_difficulty_black
        return current_ai.get_best_move(self.game, difficulty)
    
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
     - Slider/spinner: Difficulty (1–20)
   - If "AI vs AI":
     - Dropdown (Engine 1): Stockfish, Random, etc.
     - Slider (Difficulty 1): 1–20
     - Dropdown (Engine 2): Stockfish, Random, etc.
     - Slider (Difficulty 2): 1–20
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

#### Engines
- [x] Design and implement `AIEngine` base interface (`src/ai/ai.py`)
- [x] Implement `RandomAI` engine (built-in) (`src/ai/ai.py`)
- [x] Implement `SimpleHeuristicAI` engine (built-in; hand-crafted evaluation) (`src/ai/simple_heuristic_ai.py`)
- [ ] Implement `UCIEngine` wrapper (generic UCI binary support for Stockfish, Leela, etc.)

#### Controller
- [x] Extend `GameController` with `ai_white` / `ai_black` fields
- [x] Add `should_ai_move()` and `make_ai_move()` methods
- [x] Support passing engine instances to `GameController.__init__()`

#### Testing
- [x] Add unit tests for `RandomAI` (`TestGameControllerAIMode` in `src/tests/test_controller.py`)
- [x] Add unit tests for `SimpleHeuristicAI` (`src/tests/test_ai_engines.py`)
- [ ] Add unit tests for `UCIEngine` with Stockfish binary
- [ ] Add integration tests: `GameController` with Random vs Random
- [ ] Add integration tests: `GameController` with built-in vs Stockfish
- [ ] Test that all AI moves are legal in all positions

#### Configuration
- [ ] Document Stockfish binary installation (Windows/macOS/Linux paths)
- [ ] Create `config.py` with engine binary paths (or use environment variables)
- [ ] Add graceful fallback if Stockfish binary unavailable (warn user; offer Random/Heuristic only)

### Phase 2: UI
**Goal:** Setup dialog; auto-play loop; end-to-end playable

- [x] Wire `RandomAI` as Black in `app.py`; AI auto-replies after each human move
- [x] Player name labels above/below board reflect active game mode (e.g., "AI (Black)" / "Player 1")
- [x] Create Setup Dialog (`show_mode_dialog()`): Tkinter Toplevel with radio buttons (PvP, PvAI, AIvAI) and Start/Cancel buttons
- [x] Wire "New Game" and app startup to show Setup Dialog
- [x] Wire Start → initialize `GameController` via `mode_select()` with chosen mode
- [ ] Add engine selection dropdown to Setup Dialog (Random, Simple Heuristic, Stockfish; expandable)
- [ ] Add difficulty slider to Setup Dialog (1–20; maps to UCI depth)
- [ ] Add auto-play loop for AI vs AI mode
- [ ] Update status label to show "AI thinking..." during move computation
- [ ] Handle game-over during AI move (dialog triggers correctly)
- [ ] Manual testing: Player vs Stockfish, Random vs Random, Heuristic vs Stockfish

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
- [ ] Save/load AI selection to JSON (versioned format)
- [ ] Main menu with "Continue Game" option
- [ ] AI vs AI auto-play speed control (slider: instant, 1 sec/move, 2 sec/move)
- [ ] ELO display or performance metrics (optional)
- [ ] UCI engine advanced options (hash, threads, opening books)

---

## 8. Test Plan

### 8.1 Unit Tests: AI Engines

| Scenario | Test |
|---|---|
| Random engine picks legal move | Play Random on various positions; assert move is in legal moves |
| Random engine raises on stalemate | Call Random with game_over=True; expect ValueError |
| SimpleHeuristic prioritizes capture | Position with 2 legal moves (capture or quiet); assert capture chosen |
| SimpleHeuristic handles checkmate move | Position where only move is checkmate; assert that move chosen |
| Stockfish picks strong move (optional) | Play Stockfish at depth 5 vs starting position; assert e4 or d4 (standard openings) |
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
| Select "Player vs AI" | Radio button selection | AI engine dropdown and difficulty slider show |
| Start game with AI | Choose engine, difficulty, click Start | Board appears; AI plays first move after user move |
| Status updates | Play move as Player | Status shows "White's move" → "AI thinking..." → "Black's move" |
| Save game with AI | Play a few moves | Save dialog; JSON contains `"engine": "Random"`, `"difficulty": 5` |

---

## 9. Files to Create/Modify

| File | Change | Phase | Status |
|---|---|---|---|
| `src/ai/ai.py` | New: Base `AIEngine` class + `RandomAI` implementation (consolidated) | 1 | Done |
| `src/ai/simple_heuristic_ai.py` | New: `SimpleHeuristicAI` implementation | 1 | Pending |
| `src/ai/uci_engine.py` | New: Generic `UCIEngine` wrapper for Stockfish, Leela, etc. | 1 | Pending |
| `src/ai/config.py` | New: Engine paths and configuration | 1 | Pending |
| `src/ai/__init__.py` | Export engine classes | 1 | Pending |
| `src/gui/controller.py` | Update `GameController.__init__()` and add `should_ai_move()`, `make_ai_move()` | 1 | Done |
| `src/gui/app.py` | Partial (Phase 2): RandomAI wired as Black; player labels; Setup Dialog pending | 2 | Partial |
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

## 10. Acceptance Criteria

- [ ] Player can start a Player vs AI game
- [ ] Player can start an AI vs AI game
- [ ] AI engine picks a legal move in every position
- [ ] Easy AI (difficulty 1) vs Easy AI completes a full game
- [ ] Hard AI (Stockfish depth 15+) makes reasonably strong moves
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

## 11. Questions & Decisions

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

