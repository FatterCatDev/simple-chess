from utils.constants import FILES, RANKS, COLOR
from game.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class ChessBoard:
    """
    Represents a chess board and its state.
    """

    def __init__(self):
        """Initialize the chess board with pieces in their starting positions."""
        self.board = self.create_initial_blank_board()
        self.load_standard_setup()

    def create_initial_blank_board(self):
        """Create the initial setup of the chess board."""
        board = {}
        for rank in RANKS:
            for file in FILES:
                position = f"{file}{rank}"
                board[position] = None  # Initialize all positions to None                
        return board
    
    def get_piece_at(self, position):
        """Get the piece at a specific position on the board."""
        return self.board.get(position, None)
    
    def set_piece_at(self, position, piece):
        """Set a piece at a specific position on the board."""
        self.board[position] = piece

    def remove_piece_at(self, position):
        """Remove a piece from a specific position on the board."""
        self.board[position] = None

    def is_position_occupied(self, position):
        """Check if a specific position on the board is occupied by a piece."""
        if self.board.get(position) is not None:
            return True
        return False

    def move_piece(self, from_position, to_position):
        """Move a piece from one position to another."""
        if from_position not in self.board or to_position not in self.board:
            raise ValueError(f"Invalid position(s): {from_position}, {to_position}")
        
        piece = self.get_piece_at(from_position)

        if piece is None:
            raise ValueError(f"No piece at position {from_position} to move.")
        
        if self.is_position_occupied(to_position):
            self.remove_piece_at(to_position)  # Capture the piece at the destination
        
        # Move the piece
        self.set_piece_at(to_position, piece)
        self.remove_piece_at(from_position)
        piece.position = to_position
        piece.has_moved = True

    def display_board(self):
        """Display the current state of the chess board."""
        print("  " + " ".join(FILES))
        for rank in reversed(RANKS):
            row = [self.board[f"{file}{rank}"] for file in FILES]
            row_display = []
            for piece in row:
                if piece is None:
                    row_display.append(".")
                else:
                    row_display.append(str(piece))
            print(f"{rank} " + " ".join(row_display))

    def load_standard_setup(self):
        """Load the standard chess setup with all pieces in their starting positions."""
        # Place pawns
        for file in FILES:
            self.board[f"{file}2"] = Pawn(COLOR["white"], f"{file}2")
            self.board[f"{file}7"] = Pawn(COLOR["black"], f"{file}7")

        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        # Place back row pieces for white
        for i, piece_class in enumerate(back_row):
            file = FILES[i]
            self.board[f"{file}1"] = piece_class(COLOR["white"], f"{file}1")
            self.board[f"{file}8"] = piece_class(COLOR["black"], f"{file}8")
    
    def get_board_snapshot(self):
        """Get a snapshot of the current board state for threefold repetition detection."""
        snapshot = {}
        for position, piece in self.board.items():
            if piece is not None:
                snapshot[position] = (piece.type, piece.color)
            else:
                snapshot[position] = None
        return snapshot
    
    def get_square_color(self, position):
        """Determine the color of a square based on its position."""
        file = position[0]
        rank = int(position[1])
        file_index = FILES.index(file)
        return COLOR["white"] if (file_index + rank) % 2 == 0 else COLOR["black"]