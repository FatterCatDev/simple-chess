# Simple Chess - Design Document

## 1. Project Overview

### 1.1 Purpose
Learn how to create a program using Python. This is a personal learning project to develop programming skills and understand the fundamentals of building a complete application.

### 1.2 Target Audience
Personal project. This is a learning exercise for the developer.

### 1.3 Scope
A functional chess game with the following requirements:
- Cross-platform compatibility (Windows, macOS, Linux)
- Basic chess rules implementation
- Simple user interface for gameplay
- Focus on clean, maintainable Python code

---

## 2. Core Features

### 2.1 MVP (Minimum Viable Product)
<!-- List the essential features needed for a working chess game -->

- [x] Display a chess board in a Tkinter window
- [x] Move pieces with standard chess rules
- [x] Human vs Human gameplay
- [x] Game status display (check, checkmate, stalemate)
- [x] Undo/Reset game functionality
- [x] Architecture ready for AI integration

### 2.2 Future Features
<!-- Nice-to-have features for later versions -->

- [ ] AI opponent (Stockfish integration)
- [ ] Game save/load functionality
- [ ] Move history and replay
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
<!-- List the major components/modules needed -->

- **ChessBoard**: Represents the 8x8 board and piece positions
- **Piece**: Represents individual chess pieces (Pawn, Rook, Knight, etc.)
- **Game**: Manages game state, turn logic, and move validation
- **GUI/ChessApp**: Tkinter window and user interface
- **AIEngine** (Optional): Interface for chess bot integration (e.g., Stockfish)
- **MoveValidator**: Validates moves according to chess rules

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
- Move history (for undo functionality)
- Game status (active, checkmate, stalemate, check)
- Captured pieces

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
Implement the following FIDE special moves:
- **Castling** (if both King and Rook haven't moved, no pieces between them, King not in check)
- **En Passant** (Pawn capture of opponent's pawn that just moved two squares)
- **Pawn Promotion** (Pawn reaching the 8th rank promotes to Queen, Rook, Bishop, or Knight)

### 5.3 Win/Loss Conditions
- **Checkmate**: Opponent's King is in check and has no legal moves → Current player wins
- **Stalemate**: Opponent's King is NOT in check but has no legal moves → Draw
- **Resignation**: Player chooses to give up → Opponent wins
- **Draw by agreement**: Both players agree to draw
- **Insufficient material**: Neither player has enough pieces to checkmate

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
<!-- Initial project structure and basic pieces -->

- [ ] Create folder structure (gui/, game/, ai/, utils/)
- [ ] Create Piece class (base class for all pieces)
- [ ] Create specific piece classes (Pawn, Rook, Knight, Bishop, Queen, King)
- [ ] Create ChessBoard class with 8x8 grid
- [ ] Create basic Game class to manage game state
- [ ] Add piece constants and colors (White/Black)
- [ ] Create initial board setup (pieces in starting positions)
- [ ] Test data structures with print statements

### 7.2 Phase 2: Game Logic & Move Validation
<!-- Implement board and move validation -->

- [ ] Implement move validation for each piece type
- [ ] Implement blocking logic (pieces can't move through obstacles)
- [ ] Implement special moves (Castling, En Passant, Promotion)
- [ ] Implement check detection
- [ ] Implement checkmate detection
- [ ] Implement stalemate detection
- [ ] Implement move history/undo functionality
- [ ] Test game logic with unit tests

### 7.3 Phase 3: GUI & User Interaction
<!-- Add UI and player interaction -->

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
- [ ] Test GUI interactions

### 7.4 Phase 4: Polish & Distribution
<!-- Testing and refinement -->

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
│   └── rules.py      # Chess rules validator
├── ai/
│   └── engine.py     # AI engine interface (optional)
└── utils/
    └── constants.py  # Game constants
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
<!-- What needs to be tested? -->

### 9.2 Integration Tests
<!-- How components work together -->

---

## 10. Notes & References
<!-- Any additional notes or resources -->

