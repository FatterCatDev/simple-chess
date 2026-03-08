# Simple Chess - Design Document

## 1. Project Overview

### 1.1 Purpose
Learn how to create a program using Python. This is a personal learning project to develop programming skills and understand the fundamentals of building a complete application.

### 1.2 Target Audience
Personal project. This is a learning exercise for the developer.

### 1.3 Scope
A functional chess game with the following requirements:
- Cross-platform compatibility (Windows, macOS, Linux)
- Standard chess rules implementation
- Simple user interface for gameplay
- Save games in chess notation format
- Load notation and replay games step by step
- Focus on clean, maintainable Python code

---

## 2. Core Features

### 2.1 MVP (Minimum Viable Product)
- [ ] Display a chess board in a Tkinter window
- [x] Move pieces with standard chess rules
- [x] Human vs Human gameplay (core logic ready)
- [x] Game status logic (check, checkmate, stalemate, draw rules)
- [x] Reset game functionality
- [ ] Undo move functionality
- [ ] Save game to notation
- [ ] Load game from notation
- [ ] Step-by-step replay from notation
- [x] Architecture ready for AI integration

### 2.2 Current Implementation Status
- [x] All piece movement rules implemented and tested
- [x] Check detection working
- [x] Checkmate detection with automatic game end
- [x] Stalemate detection with automatic game end
- [x] Move validation prevents self-check
- [x] Special moves: castling, en passant, promotion
- [x] Draw rules: threefold repetition, fifty-move rule, insufficient material
- [x] Unit tests: 65 passing (2 skipped)
- [ ] Move notation history (SAN/PGN-like) not implemented yet

### 2.3 Future Features
- [ ] AI opponent (Stockfish integration)
- [ ] Different difficulty levels for AI
- [ ] Timer for timed games
- [ ] Custom themes and board colors

---

## 3. Architecture

### 3.1 System Design
Modular architecture with clear separation of concerns:
- **GUI Layer** (Tkinter) - Handles user interaction and display
- **Game Logic Layer** - Chess rules, board state, move validation
- **AI Layer** (Optional) - Chess engine integration (e.g., Stockfish)
- **Data Layer** - Board representation and game state management

This design allows for easy swapping of AI engines or game modes without affecting the GUI or core logic.

### 3.2 Main Components
- **ChessBoard**: Represents the 8x8 board and piece positions
- **Piece**: Represents individual chess pieces (Pawn, Rook, Knight, etc.)
- **Game**: Manages game state, turn logic, and move validation
- **StandardChessRules**: Piece movement and special-move legality checks
- **GUI/ChessApp**: Tkinter window and user interface
- **AIEngine** (Optional): Interface for chess bot integration (e.g., Stockfish)
- **Notation Builder**: Generates move notation history from validated moves
- **Notation Parser**: Reads stored notation and converts it into executable moves
- **Replay Controller**: Supports stepping forward/backward through saved moves

### 3.3 Data Flow
User clicks on board → GUI captures event → Game validates move → Board updates → AI makes move (if enabled) → GUI refreshes display

---

## 4. Data Structures

### 4.1 Board Representation
The chess board will be drawn using Tkinter canvas lines:
- 8x8 grid drawn with black lines on a light canvas background
- Each square is clickable and responds to mouse events
- Squares can be highlighted to show valid moves
- Canvas coordinates map to chess board positions (a1-h8)

### 4.2 Piece Representation
Pieces will be represented as sprite images on the canvas:
- Each piece type (Pawn, Rook, Knight, Bishop, Queen, King) has a sprite image
- Sprites are positioned on the board based on piece data
- Pieces can be selected and dragged (visual feedback)
- Sprites can be highlighted or grayed out based on game state

### 4.3 Game State
Game state tracks:
- Current board position (which piece is on which square)
- Whose turn it is (White or Black)
- Last move metadata (for en passant and future notation)
- Draw tracking state (halfmove clock, repetition history)
- Game status (active, check, checkmate, stalemate, draw)
- Captured pieces
- Notation move history
- Replay cursor/index for step-by-step navigation

---

## 5. Game Rules & Logic

### 5.1 Movement Rules
All piece movements follow standard FIDE (International Chess Federation) rules:
- **Pawn**: Moves 1 square forward (2 on first move), captures diagonally forward
- **Rook**: Moves any number of squares horizontally or vertically
- **Knight**: Moves in L-shape (2+1 or 1+2 squares)
- **Bishop**: Moves any number of squares diagonally
- **Queen**: Moves any number of squares in any direction (horizontal, vertical, diagonal)
- **King**: Moves 1 square in any direction

No pieces can move through other pieces (except Knight).

### 5.2 Special Moves
Implemented FIDE special moves:
- **Castling**
- **En Passant**
- **Pawn Promotion**

### 5.3 Win/Loss Conditions
- **Checkmate**: Opponent's King is in check and has no legal moves → Current player wins
- **Stalemate**: Opponent's King is NOT in check but has no legal moves → Draw
- **Threefold repetition**: Same position repeated three times → Draw
- **Fifty-move rule**: 100 half-moves without pawn move/capture → Draw
- **Insufficient material**: Neither player has enough pieces to checkmate → Draw
- **Resignation** (planned)
- **Draw by agreement** (planned)

---

## 6. User Interface

### 6.1 UI Design
Simple graphical window-based interface that launches when the user runs the executable:
- **Windows**: Launches from .EXE file
- **macOS**: Launches from .APP application package
- **Linux**: Launches from executable or application launcher
The window will display the chess board and game interface with no command-line interaction required.

### 6.2 User Interactions
- Click on chess pieces to select them
- Click on valid destination squares to move pieces
- Visual feedback for valid moves
- Pop-up dialogs for game events (checkmate, promotion, etc.)
- **Help button**: Opens a dialog displaying game rules and piece movements
- Game status display showing current turn, check status, game outcome

---

## 7. Implementation Plan

### 7.1 Phase 1: Project Setup & Core Data Structures
- [x] Create folder structure (gui/, game/, ai/, utils/)
- [x] Create Piece class (base class for all pieces)
- [x] Create specific piece classes (Pawn, Rook, Knight, Bishop, Queen, King)
- [x] Create ChessBoard class with 8x8 grid
- [x] Create basic Game class to manage game state
- [x] Add piece constants and colors (White/Black)
- [x] Create initial board setup (pieces in starting positions)
- [x] Test data structures with print statements

### 7.2 Phase 2: Game Logic & Move Validation
- [x] Implement move validation for each piece type
- [x] Implement blocking logic (pieces can't move through obstacles)
- [x] Implement special moves (Castling, En Passant, Promotion)
- [x] Implement check detection
- [x] Implement checkmate detection
- [x] Implement stalemate detection
- [x] Implement draw rules (threefold, fifty-move, insufficient material)
- [x] Test game logic with unit tests (65 passing, 2 skipped)

### 7.3 Phase 2.5: Notation Builder (Next)
- [ ] Define notation scope (SAN-lite vs full SAN)
- [ ] Add move history storage in `Game`
- [ ] Record notation per successful move
- [ ] Support notation for:
    - [ ] normal moves and captures
    - [ ] castling (`O-O`, `O-O-O`)
    - [ ] en passant captures
    - [ ] promotions (`=Q`, `=R`, `=B`, `=N`)
    - [ ] check (`+`) and checkmate (`#`)
- [ ] Add unit tests for notation output
- [ ] Export notation history to file

### 7.35 Phase 2.6: Notation Import and Replay (Required)
- [ ] Parse saved notation into move sequence
- [ ] Validate parsed moves against game rules
- [ ] Build replay state from parsed moves
- [ ] Implement replay controls: start, previous, next, end
- [ ] Show current move number and notation during replay
- [ ] Add unit/integration tests for import and replay flows

### 7.4 Phase 3: GUI & User Interaction

- [ ] Create Tkinter main window
- [ ] Draw chess board (8x8 grid with lines)
- [ ] Draw chess pieces using Unicode symbols
- [ ] Implement click detection on squares
- [ ] Implement piece selection and highlighting
- [ ] Implement valid move highlighting
- [ ] Implement move execution via GUI clicks
- [ ] Add status bar (current turn, game status)
- [ ] Add buttons (New Game, Undo, Reset)
- [ ] Add Rules/Help dialog
- [ ] Add game over dialog (Checkmate/Stalemate)
- [ ] Add pawn promotion dialog
- [ ] Add notation panel/move list
- [ ] Add save notation button
- [ ] Add load notation button
- [ ] Add replay controls (Prev/Next/Play/Pause)
- [ ] Test GUI interactions

### 7.5 Phase 4: Polish & Distribution

- [ ] Code review and refactoring
- [ ] Add comprehensive comments
- [ ] Test on Windows, macOS, and Linux
- [ ] Create .gitignore entries for build files
- [ ] Create executable for Windows (.exe)
- [ ] Create executable for macOS (.app)
- [ ] Create executable for Linux (binary)
- [ ] Final testing on all platforms
- [ ] Update README with how to run executables

---

## 8. Technical Decisions

### 8.1 Language & Libraries
- **Language**: Python 3.8+
- **GUI Framework**: Tkinter (built-in)
- **Optional Dependencies**: python-chess (chess logic helpers), stockfish (AI engine - future feature)
- **Cross-platform**: No OS-specific dependencies required

### 8.2 Code Organization
Project structure:
```
src/
├── main.py           # Entry point
├── gui/
│   └── chess_app.py  # Tkinter GUI
├── game/
│   ├── board.py      # Board representation
│   ├── piece.py      # Piece classes
│   ├── game.py       # Game logic
│   └── standard_chess_rules.py  # Chess rules validator
├── ai/
│   └── engine.py     # AI engine interface (optional)
└── utils/
    └── constants.py  # Game constants
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Piece movement legality
- Special moves (castling, en passant, promotion)
- Check/checkmate/stalemate detection
- Draw conditions (threefold repetition, fifty-move, insufficient material)
- Notation output (next phase)

### 9.2 Integration Tests
- End-to-end move sequences (opening patterns, checkmates, draws)
- GUI interaction tests (after UI phase)

---

## 10. Notes & References
- Current immediate priority: notation builder, notation import, and replay support in the game layer.
- Keep engine logic deterministic and test-first as notation features are added.

