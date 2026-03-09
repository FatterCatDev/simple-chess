from game.game import Game

class GameController:
    def __init__(self, game: Game):
        self.game = game
        self.selected_square = None
        self.last_error = None

    def get_state(self):
        """Return the current state of the game."""
        game_state = { # Temporary placeholder for the game state representation
            "board": self.build_board_state(),
            "current_turn": self.game.current_turn,
            "selected_square": self.selected_square,
            "legal_moves": self.game.get_legal_moves(self.selected_square) if self.selected_square else [],
            "game_over": self.game.game_over,
            "is_draw": self.game.is_draw,
            "draw_reason": self.game.draw_reason,
            "is_in_check": self.game.is_in_check,
            "move_list": [move["san"] for move in self.game.move_history],         # SAN strings
            "replay": {
                "active": self.game.replay_active,
                "index": self.game.replay_index,
                "total": len(self.game.replay_notation)
            },
            "last_error": self.last_error           # for invalid UI actions
        }
        return game_state
    
    def select_square(self, position):
        """Select a square on the board."""
        piece = self.game.board.get_piece_at(position)
        if piece and piece.color == self.game.current_turn:
            self.selected_square = position
            return True
        return False
    
    def try_move(self, to_position):
        """Attempt to move a piece from one position to another."""
        if self.selected_square:
            from_position = self.selected_square
            try:
                self.game.make_move(from_position, to_position)
                self.selected_square = None
                return True
            except ValueError as e:
                print(f"Invalid move: {e}")
                self.last_error = str(e)
                self.selected_square = None
                return False
        return False
    
    def undo(self):
        """Undo the last move."""
        pass # This method will be implemented to handle undoing the last move, including updating the game state and board.
    
    def reset(self):
        """Reset the game to its initial state."""
        pass # This method will be implemented to reset the game, including clearing the board, resetting the turn, and clearing move history.
    
    def load_notation(self, notation):
        """Load a game from SAN-lite notation."""
        pass
    
    def replay_start(self):
        """Start replaying the game from the beginning."""
        pass # This method will be implemented to initiate replay mode, resetting the game state to the beginning of the move list.

    def replay_next(self):
        """Replay the next move in the game."""
        pass # This method will be implemented to advance the replay to the next move, updating the game state and board accordingly.
    
    def replay_previous(self):
        """Replay the previous move in the game."""
        pass # This method will be implemented to go back to the previous move in the replay, updating the game state and board accordingly.

    def replay_end(self):
        """Replay the game to the end."""
        pass # This method will be implemented to fast-forward the replay to the end of the move list, updating the game state and board accordingly.

    def on_square_click(self, position):
        """Handle a square click event from the GUI."""
        if not self.selected_square:
            if self.select_square(position):
                self.selected_square = position
            else:
                self.selected_square = None
        else:
            color_of_clicked_piece = self.game.board.get_piece_at(position).color if self.game.board.get_piece_at(position) else None
            if color_of_clicked_piece == self.game.current_turn and position != self.selected_square:
                # If the clicked square has a piece of the current turn, select it
                self.selected_square = position
            else:
                if self.try_move(position):
                    self.selected_square = None
                else:
                    # If the move was invalid, keep the selection or clear it based on your design choice
                    self.selected_square = None  # or keep it as self.selected_square

    def build_board_state(self):
        """Build a representation of the board state for the GUI."""
        board_state = {}
        for position, piece in self.game.board.board.items():
            if piece:
                board_state[position] = piece.color[0].lower() + piece.type[0].upper()  # e.g., 'wP' for white pawn
            else:
                board_state[position] = None
        return board_state