from .board import ChessBoard
from .standard_chess_rules import StandardChessRules
from utils.constants import COLOR

class Game:
    def __init__(self):
        self.board = ChessBoard()
        self.rules = StandardChessRules(self.board)
        self.current_turn = COLOR["white"]  # White starts first
        self.game_over = False
        self.last_move = None   # Initialize last_move to None
                                # "piece_type": piece.type,
                                # "piece_color": piece.color,
                                # "from": from_position,
                                # "to": to_position,
                                # "captured_piece": captured_piece if captured_piece else None,
                                # "was_two_square_pawn_move": was_two_square_pawn_move

    def make_move(self, from_position, to_position):
        """Make a move on the board if it's valid."""
        castled = False
        en_passant = False
        if self.game_over:
            raise ValueError("The game is over. No more moves can be made.")
        
        piece = self.board.get_piece_at(from_position)
        captured_piece = self.board.get_piece_at(to_position)
        if piece is None:
            raise ValueError(f"No piece at position {from_position} to move.")
        
        if piece.color != self.current_turn:
            raise ValueError(f"It's {self.current_turn}'s turn. Cannot move {piece.color}'s piece.")
        
        if piece.type == "K" and abs(ord(from_position[0]) - ord(to_position[0])) == 2 and from_position[1] == to_position[1]:
            if self.can_castle(piece.color, "kingside") and to_position == f"g{from_position[1]}":
                # Handle kingside castling
                self.perform_castling(piece.color, "kingside")
                castled = True
            elif self.can_castle(piece.color, "queenside") and to_position == f"c{from_position[1]}":
                # Handle queenside castling
                self.perform_castling(piece.color, "queenside")
                castled = True
            else:
                raise ValueError(f"Invalid move from {from_position} to {to_position}.")
        else:
            if not self.rules.is_valid_move(from_position, to_position, self.last_move):
                raise ValueError(f"Invalid move from {from_position} to {to_position}.")
            
            #check for en passant capture
            if piece.type == "P" and self.last_move and self.last_move["was_two_square_pawn_move"]:
                if self.rules.is_en_passant_possible(piece.position, to_position, self.last_move):
                    en_passant = True
            
            if self.would_be_in_check_after_move(from_position, to_position):
                raise ValueError(f"Move from {from_position} to {to_position} would put {self.current_turn} in check.")
        
        if not castled:
            self.board.move_piece(from_position, to_position)
            if en_passant:
                # Remove the captured pawn in en passant
                captured_pawn_position = f"{to_position[0]}{from_position[1]}"
                captured_piece = self.board.get_piece_at(captured_pawn_position)  # Update captured_piece for last_move record
                self.board.remove_piece_at(captured_pawn_position)

        self._record_last_move(piece, from_position, to_position, captured_piece, piece.type == "P" and abs(int(from_position[1]) - int(to_position[1])) == 2)

        if self.in_check(self.opponent_color()):
            if self.checkmate(self.opponent_color()):
                self.game_over = True
                print(f"Checkmate! {self.current_turn} wins.")
            else:
                print(f"{self.opponent_color()} is in check.")
        
        if self.stalemate(self.opponent_color()):
            self.game_over = True
            print("Stalemate! The game is a draw.")
                
        if not self.game_over:
            self.switch_turn()



    def switch_turn(self):
        """Switch the turn to the other player."""
        self.current_turn = COLOR["black"] if self.current_turn == COLOR["white"] else COLOR["white"]

    def in_check(self, color):
        """Check if the specified color is in check."""
        king_pos = self.find_king(color)
        for position, piece in self.board.board.items():
            if piece and piece.color == self.opponent_color(color):
                if self.rules.is_valid_move(position, king_pos):
                    return True
        return False
    
    def checkmate(self, color):
        """Check if the specified color is in checkmate."""
        if not self.in_check(color):
            return False  # Not in check, so cannot be in checkmate
        valid_moves = self.get_all_valid_moves(color)
        return len(valid_moves) == 0
    
    def stalemate(self, color):
        """Check if the specified color is in stalemate."""
        if self.in_check(color):
            return False  # In check, so cannot be in stalemate
        valid_moves = self.get_all_valid_moves(color)
        return len(valid_moves) == 0
    
    def reset_game(self):
        """Reset the game to the initial state."""
        self.board = ChessBoard()
        self.rules = StandardChessRules(self.board)
        self.current_turn = COLOR["white"]
        self.game_over = False
        self.last_move = None

    def find_king(self, color):
        """Find the king piece of the specified color."""
        for position, piece in self.board.board.items():
            if piece and piece.color == color and piece.type == "K":
                return position
        raise ValueError(f"No king found for color {color}.")
    
    def opponent_color(self, color=None):
        """Get the opponent's color."""
        if color is None:
            color = self.current_turn
        return COLOR["black"] if color == COLOR["white"] else COLOR["white"]
    
    def would_be_in_check_after_move(self, from_position, to_position):
        """Check if making a move would put the current player in check."""
        piece = self.board.get_piece_at(from_position)
        if piece is None:
            raise ValueError(f"No piece at position {from_position} to move.")
        
        # Save the current state of the board and piece positions
        original_piece_has_moved = piece.has_moved
        captured_piece = self.board.get_piece_at(to_position)
        
        # Temporarily make the move
        self.board.move_piece(from_position, to_position)
        
        in_check = self.in_check(piece.color)
        
        # Undo the move
        self.board.set_piece_at(from_position, piece)
        self.board.set_piece_at(to_position, captured_piece)
        piece.position = from_position
        piece.has_moved = original_piece_has_moved
        if captured_piece:
            captured_piece.position = to_position  # Restore captured piece's position if it was captured
        
        return in_check
    
    def get_all_valid_moves(self, color):
        """Get all valid moves for the specified color."""
        valid_moves = []
        for from_position, piece in self.board.board.items():
            if piece and piece.color == color:
                for to_position in self.board.board.keys():
                    if self.rules.is_valid_move(from_position, to_position):
                        if not self.would_be_in_check_after_move(from_position, to_position):
                            valid_moves.append((from_position, to_position))
            if piece and piece.color == color and piece.type == "K":
                rank = "1" if color == COLOR["white"] else "8"
                if from_position == f"e{rank}":
                    if self.can_castle(color, "kingside"):
                        valid_moves.append((from_position, f"g{rank}"))
                    if self.can_castle(color, "queenside"):
                        valid_moves.append((from_position, f"c{rank}"))
        return valid_moves
    
    def can_castle(self, color, side):
        """Check if the specified color can castle on the given side ('kingside' or 'queenside')."""
        if self.in_check(color):
            return False  # Cannot castle while in check
        
        rank = '1' if color == COLOR["white"] else '8'
        king_position = f"e{rank}"
        rook_position = f"h{rank}" if side == 'kingside' else f"a{rank}"
        
        king = self.board.get_piece_at(king_position)
        rook = self.board.get_piece_at(rook_position)
        
        if not king or not rook:
            return False  # King or rook is missing
        
        if king.has_moved or rook.has_moved:
            return False  # King or rook has already moved
        
        if king.color != color or rook.color != color:
            return False  # King or rook is not the correct color
        
        if king.type != "K" or rook.type != "R":
            return False  # King or rook is not the correct piece type
        
        # Check if squares between king and rook are empty
        files_between = ['f', 'g'] if side == 'kingside' else ['b', 'c', 'd']
        for file in files_between:
            position = f"{file}{rank}"
            if self.board.is_position_occupied(position):
                return False  # Square is occupied
        
        # Check if squares the king passes through are under attack
        king_path_positions = [f"e{rank}", f"f{rank}", f"g{rank}"] if side == 'kingside' else [f"e{rank}", f"d{rank}", f"c{rank}"]
        for position in king_path_positions:
            if self.is_square_under_attack(position, self.opponent_color(color)):
                return False  # Square is under attack
        
        return True
    
    def is_square_under_attack(self, position, attacking_color):
        """Check if a specific square is under attack by the specified color."""
        for from_position, piece in self.board.board.items():
            if piece and piece.color == attacking_color:
                if self.rules.is_valid_move(from_position, position):
                    return True
                elif piece.type == "P":  # Special case for pawn attacks
                    if self.rules.is_valid_pawn_attack(piece, from_position, position):
                        return True
        return False
    
    def perform_castling(self, color, side):
        """Perform castling for the specified color and side ('kingside' or 'queenside')."""
        rank = '1' if color == COLOR["white"] else '8'
        king_position = f"e{rank}"
        rook_position = f"h{rank}" if side == 'kingside' else f"a{rank}"
        
        king = self.board.get_piece_at(king_position)
        rook = self.board.get_piece_at(rook_position)
        
        if not king or not rook:
            raise ValueError("Cannot castle: King or Rook is missing.")
        
        if side == 'kingside':
            new_king_position = f"g{rank}"
            new_rook_position = f"f{rank}"
        else:  # queenside
            new_king_position = f"c{rank}"
            new_rook_position = f"d{rank}"
        
        # Move the king and rook to their new positions
        self.board.move_piece(king_position, new_king_position)
        self.board.move_piece(rook_position, new_rook_position)

    def _build_last_move(self, piece, from_position, to_position, captured_piece = None, was_two_square_pawn_move = False):
        """Build the last move dictionary."""
        return {
            "piece_type": piece.type,
            "piece_color": piece.color,
            "from": from_position,
            "to": to_position,
            "captured_piece": captured_piece if captured_piece else None,
            "was_two_square_pawn_move": was_two_square_pawn_move
        }
    
    def _record_last_move(self, piece, from_position, to_position, captured_piece = None, was_two_square_pawn_move = False):
        """Store the last move in the game state."""
        self.last_move = self._build_last_move(piece, from_position, to_position, captured_piece, was_two_square_pawn_move)