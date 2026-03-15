from game.game import Game
from utils.constants import COLOR, FILES, RANKS
import json

class GameController:
    def __init__(self, game: Game, ai_white=None, ai_black=None):
        self.game = game
        self.selected_square = None
        self.last_error = None
        self.history_list = []  # Store the full move list for GUI display
        self._sync_history_list()  # Initialize the history list with the current game state
        self.ai_white = ai_white
        self.ai_black = ai_black

    def get_state(self):
        """Return the current state of the game."""
        game_state = { # Temporary placeholder for the game state representation
            "board": self.build_board_state(),
            "current_turn": self.game.current_turn,
            "selected_square": self.selected_square,
            "legal_moves": self.game.get_legal_moves(self.selected_square) if self.selected_square else [],
            "previous_from": self.game.last_move["from"] if self.game.last_move else None,
            "previous_to": self.game.last_move["to"] if self.game.last_move else None,
            "game_over": self.game.game_over,
            "is_draw": self.game.is_draw,
            "draw_reason": self.game.draw_reason,
            "is_in_check": self.game.is_in_check,
            "move_list": self.history_list,         # SAN strings
            "replay": {
                "active": self.game.replay_active,
                "index": self.game.replay_index,
                "total": len(self.game.replay_notation)
            },
            "last_error": self.last_error,           # for invalid UI actions
        }
        return game_state
    
    def select_square(self, position):
        """Select a square on the board."""
        piece = self.game.board.get_piece_at(position)
        if piece and piece.color == self.game.current_turn:
            self.selected_square = position
            return True
        return False
    
    def try_move(self, to_position, promotion_choice="Q"):
        """Attempt to move a piece from one position to another."""
        if self.selected_square:
            from_position = self.selected_square
            if self.game.replay_active and self.game.replay_index < len(self.game.replay_notation):
                self.last_error = "Cannot make moves while not at the end of replaying."
                self.selected_square = None
                return False

            try:
                self.game.make_move(from_position, to_position, promotion_choice)
                self._sync_history_list()  # Update the history list after a successful move
                self.selected_square = None
                if self.game.replay_active:
                    self.game.replay_active = False  # Exit replay mode if a move is attempted
                    self.game.replay_notation = []  # Clear replay notation
                    self.game.replay_index = 0  # Reset replay index
                return True
            except ValueError as e:
                print(f"Invalid move: {e}")
                self.last_error = str(e)
                self.selected_square = None
                return False
        return False
    
    def undo(self):
        """Undo the last move."""
        try:
            if self.game.replay_active:
                raise ValueError("Cannot undo moves while in replay mode.")
            self.game.undo_move()
            self.selected_square = None  # Clear selection after undo
            self.last_error = None  # Clear last error after undo
            self._sync_history_list()  # Update the history list after undo
        except ValueError as e:
            print(f"Cannot undo: {e}")
            self.last_error = str(e)
    
    def reset(self):
        """Reset the game to its initial state."""
        self.game.reset_game()
        self.selected_square = None
        self.last_error = None  # Clear last error on reset
        self._sync_history_list()  # Update the history list after reset
    
    def load_notation(self, notation):
        """Load a game from SAN-lite notation."""
        try:
            self.game.load_notation(notation)
            self.selected_square = None
            self.last_error = None
            self._sync_history_list()  # Update the history list after loading notation
            return True
        except ValueError as e:
            self.last_error = str(e)
            return False
    
    def replay_start(self):
        """Start replaying the game from the beginning."""
        try:
            if self.game.replay_notation:
                notation = self.game.replay_notation
            else:
                notation = self.game.export_notation()
            if not notation:
                raise ValueError("No moves available to replay.")
            self.history_list = notation.copy()  # Store the full move list for GUI display
            self.game.replay_start(notation)
            self.selected_square = None
            self.last_error = None
            return True
        except ValueError as e:
            self.last_error = str(e)
            return False

    def replay_next(self):
        """Replay the next move in the game."""
        try:
            if not self.game.replay_notation:
                notation = self.game.export_notation()
                self.history_list = notation.copy()  # Store the full move list for GUI display
                if not notation:
                    raise ValueError("No moves available to replay.")
                self.game.replay_start(notation)
            self.game.replay_next()
            self.selected_square = None
            self.last_error = None
            return True
        except ValueError as e:
            self.last_error = str(e)
            return False
    
    def replay_previous(self):
        """Replay the previous move in the game."""
        try:
            if not self.game.replay_notation:
                notation = self.game.export_notation()
                self.history_list = notation.copy()  # Store the full move list for GUI display
                if not notation:
                    raise ValueError("No moves available to replay.")
                self.game.replay_start(notation)
            self.game.replay_previous()
            self.selected_square = None
            self.last_error = None
            return True
        except ValueError as e:
            self.last_error = str(e)
            return False

    def replay_end(self):
        """Replay the game to the end."""
        try:
            if not self.game.replay_notation:
                notation = self.game.export_notation()
                self.history_list = notation.copy()  # Store the full move list for GUI display
                if not notation:
                    raise ValueError("No moves available to replay.")
                self.game.replay_start(notation)
            self.game.replay_end()
            self.selected_square = None
            self.last_error = None
            return True
        except ValueError as e:
            self.last_error = str(e)
            return False

    def on_square_click(self, position):
        """Handle a square click event from the GUI."""
        self.last_error = None  # Clear last error on new action
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
                    return True  # Move was successful
                else:
                    # If the move was invalid, keep the selection or clear it based on your design choice
                    self.selected_square = None  # or keep it as self.selected_square
        return False  # Move was not successful or no move attempted        

    def build_board_state(self):
        """Build a representation of the board state for the GUI."""
        board_state = {}
        for position, piece in self.game.board.board.items():
            if piece:
                board_state[position] = piece.color[0].lower() + piece.type[0].upper()  # e.g., 'wP' for white pawn
            else:
                board_state[position] = None
        return board_state
    
    def _sync_history_list(self):
        """Sync the history list with the game's move history."""
        self.history_list = [move["san"] for move in self.game.move_history]

    def save_notation_to_file(self, path):
        """Save the current game's SAN-lite notation to a file."""
        self.last_error = None  # Clear last error on new action
        if self.game.replay_active and self.game.replay_notation:
            notation = self.game.replay_notation
        else:
            notation = self.game.export_notation()
        if not notation:
            self.last_error = "No moves to save."
            return False
        payload = {
            "format": "san-lite-list",
            "version": 1,
            "moves": notation
        }
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            return True
        except IOError as e:
            self.last_error = f"Failed to save notation: {e}"
            return False
        
    def load_notation_from_file(self, path):
        """Load a game's SAN-lite notation from a file."""
        self.last_error = None  # Clear last error on new action
        try:
            with open(path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                moves = payload.get("moves")
                if moves is None:
                    self.last_error = "Invalid notation file: 'moves' key not found."
                    return False
                if not isinstance(moves, list):
                    self.last_error = "Invalid moves format in the file."
                    return False
                if moves == []:
                    self.last_error = "No moves found in the file."
                    return False
                if not all(isinstance(move, str) for move in moves):
                    self.last_error = "Invalid move format in the file."
                    return False
        except (IOError, ValueError) as e:
            self.last_error = f"Failed to load notation: {e}"
            return False
        return self.load_notation(moves)
    
    def should_ai_move(self):
        """Determine if it's the AI's turn to move."""
        ai = self.ai_white if self.game.current_turn == COLOR["white"] else self.ai_black
        return ai is not None and not self.game.game_over
    
    def make_ai_move(self):
        """Make a move for the AI if it's the AI's turn."""
        ai = self.ai_white if self.game.current_turn == COLOR["white"] else self.ai_black
        if ai is None or self.game.game_over:
            return False

        move = ai.get_move(self.game)
        if move is None:
            return False

        if not isinstance(move, tuple) or len(move) != 2:
            self.last_error = f"Invalid AI move format: {move}"
            return False

        from_sq, to_sq = move
        if not isinstance(from_sq, str) or len(from_sq) != 2 or from_sq[0] not in FILES or from_sq[1] not in RANKS:
            self.last_error = f"Invalid from_square: {from_sq}"
            return False
        if not isinstance(to_sq, str) or len(to_sq) != 2 or to_sq[0] not in FILES or to_sq[1] not in RANKS:
            self.last_error = f"Invalid to_square: {to_sq}"
            return False

        if not self.select_square(from_sq):
            self.last_error = f"AI selected invalid source square: {from_sq}"
            return False

        return self.try_move(to_sq)