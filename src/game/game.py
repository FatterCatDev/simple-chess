from game import piece

from .board import ChessBoard
from .standard_chess_rules import StandardChessRules
from utils.constants import COLOR
from game.piece import Queen, Rook, Bishop, Knight, Pawn

class Game:
    def __init__(self, enable_fifty_move_rule=True):
        self.enable_fifty_move_rule = enable_fifty_move_rule  # Flag to enable or disable the fifty-move rule
        self._init_game_state()  # Initialize the game state


    def _init_game_state(self):
        """Initialize or reset the game state."""
        self.board = ChessBoard()
        self.rules = StandardChessRules(self.board)
        self.current_turn = COLOR["white"]
        self.game_over = False
        self.is_draw = False
        self.draw_reason = None
        self.halfmove_clock = 0
        self.position_history = []
        self.is_in_check = False
        self.last_move = None
        self.move_history = []
        self.piece_first_move_status = False
        self.replay_notation = []  # Store the notation of moves for replay purposes
        self.replay_index = 0  # Index to track the current move in replay mode
        self.replay_active = False  # Flag to indicate if replay mode is active

    def make_move(self, from_position, to_position, promotion_choice="Q"):
        """Make a move on the board if it's valid."""
        move_information = {}
        castled = False
        en_passant = False
        pre_move_is_in_check = self.is_in_check  # Store the check status before the move for undo functionality
        self.is_in_check = False  # Reset check status at the start of the move
        pre_move_halfmove_clock = self.halfmove_clock  # Store the halfmove clock before the move for undo functionality

        if self.game_over:
            raise ValueError("The game is over. No more moves can be made.")
        
        piece = self.board.get_piece_at(from_position)
        captured_piece = self.board.get_piece_at(to_position)
        if piece is None:
            raise ValueError(f"No piece at position {from_position} to move.")
        
        if piece.color != self.current_turn:
            raise ValueError(f"It's {self.current_turn}'s turn. Cannot move {piece.color}'s piece.")
        
        self.piece_first_move_status = piece.has_moved
        
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

        # Handle pawn promotion
        was_promotion = False
        if piece.type == "P":
            promotion_rank = 8 if piece.color == COLOR["white"] else 1
            if int(to_position[1]) == promotion_rank:
                self.promotion(to_position, promotion_choice)
                was_promotion = True

        # Check for check, checkmate, and stalemate
        is_checkmate = False
        target_color = self.opponent_color()

        self.log_position()  # Log the current position for threefold repetition detection
        self.halfmove_clock = self.halfmove_clock + 1 if piece.type != "P" and captured_piece is None else 0
        if self.in_check(target_color): # Check if the opponent is in check after the move
            if self.checkmate(target_color):
                self.game_over = True
                is_checkmate = True
            else:
                self.is_in_check = True
                is_checkmate = False
        elif self.stalemate(target_color):
            self.game_over = True
            self.is_draw = True
            self.draw_reason = "Stalemate"
            is_checkmate = False
        
        if self.check_threefold_repetition(): # Check for threefold repetition draw
            self.game_over = True
            self.is_draw = True
            self.draw_reason = "Threefold repetition"
            is_checkmate = False
        elif self.enable_fifty_move_rule and self.halfmove_clock >= 100:
            self.game_over = True
            self.is_draw = True
            self.draw_reason = "Fifty-move rule"
            is_checkmate = False
        elif self.check_insufficient_material():
            self.game_over = True
            self.is_draw = True
            self.draw_reason = "Insufficient material"
            is_checkmate = False
        
        move_info = {
            "piece": piece,
            "from": from_position,
            "to": to_position,
            "captured_piece": captured_piece,
            "was_castling": castled,
            "was_promotion": was_promotion,
            "promotion_choice": promotion_choice,
            "was_en_passant": en_passant,
            "is_draw": self.is_draw,
            "is_in_check": self.is_in_check,
            "is_checkmate": is_checkmate
        }

        self.move_history.append({
            "san": self.generate_san_lite(**move_info),
            "from": from_position,
            "to": to_position,
            "piece_type": piece.type,
            "piece_color": piece.color,
            "captured_piece_type": captured_piece.type if captured_piece else None,
            "captured_piece_has_moved": captured_piece.has_moved if captured_piece else None,
            "captured_piece_color": captured_piece.color if captured_piece else None,
            "promotion_choice": promotion_choice,
            "was_castling": castled,
            "was_en_passant": en_passant,
            "was_two_square_pawn_move": piece.type == "P" and abs(int(from_position[1]) - int(to_position[1])) == 2,
            "is_in_check": self.is_in_check,
            "draw_reason": self.draw_reason,
            "last_move": self.last_move,
            "halfmove_clock": self.halfmove_clock,
            "pre_move_halfmove_clock": pre_move_halfmove_clock,
            "position_history": self.position_history.copy(),
            "current_turn": self.current_turn,
            "piece_first_move_status": self.piece_first_move_status,
            "was_promotion": was_promotion,
            "pre_move_is_in_check": pre_move_is_in_check,
        })

        self._record_last_move(piece, from_position, to_position, captured_piece, piece.type == "P" and abs(int(from_position[1]) - int(to_position[1])) == 2)
                
        if not self.game_over:
            self.switch_turn()

        return self.move_history[-1]  # Return the last move made
        # print(f"The game ended in a draw due to {self.draw_reason}.")


    def switch_turn(self):
        """Switch the turn to the other player."""
        self.current_turn = COLOR["black"] if self.current_turn == COLOR["white"] else COLOR["white"]

    def in_check(self, color):
        """Check if the specified color is in check."""
        king_pos = self.find_king(color)
        for position, piece in self.board.board.items():
            if piece and piece.color == self.opponent_color(color):
                if self.rules.is_valid_move(position, king_pos, self.last_move):
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
        self._init_game_state()  # Reinitialize the game state to start a new game

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

        # Check if en passant capture is happening
        en_passant_capture = None
        en_passant_position = None
        if piece.type == "P" and self.last_move and self.last_move["was_two_square_pawn_move"]:
            if self.rules.is_en_passant_possible(piece.position, to_position, self.last_move):
                en_passant_position = f"{to_position[0]}{from_position[1]}"
                en_passant_capture = self.board.get_piece_at(en_passant_position)
                self.board.remove_piece_at(en_passant_position)  # Temporarily remove the captured pawn for the check test
        
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
        if en_passant_capture and en_passant_position:
            self.board.set_piece_at(en_passant_position, en_passant_capture)  # Restore captured pawn in en passant
            en_passant_capture.position = en_passant_position  # Restore captured pawn's position
        
        return in_check
    
    def get_all_valid_moves(self, color):
        """Get all valid moves for the specified color."""
        valid_moves = []
        for from_position, piece in self.board.board.items():
            if piece and piece.color == color:
                for to_position in self.board.board.keys():
                    if self.rules.is_valid_move(from_position, to_position, self.last_move):
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
                if piece.type == "P":  # Special case for pawn attacks
                    if self.rules.is_valid_pawn_attack(piece, from_position, position):
                        return True
                else:
                    if self.rules.is_valid_move(from_position, position, self.last_move):
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

    def promotion(self, pawn_position, new_piece_type = "Q"):
        """Promote a pawn to a new piece type."""
        pawn = self.board.get_piece_at(pawn_position)
        if not pawn or pawn.type != "P":
            raise ValueError(f"No pawn at position {pawn_position} to promote.")
        
        rank = int(pawn_position[1])
        if (pawn.color == COLOR["white"] and rank != 8) or (pawn.color == COLOR["black"] and rank != 1):
            raise ValueError(f"Pawn at position {pawn_position} is not in the promotion rank.")
        
        # Create the new piece based on the specified type
        match new_piece_type:
            case "Q":
                new_piece = Queen(pawn.color, pawn_position)
            case "R":
                new_piece = Rook(pawn.color, pawn_position)
            case "B":
                new_piece = Bishop(pawn.color, pawn_position)
            case "N":
                new_piece = Knight(pawn.color, pawn_position)
            case _:
                raise ValueError(f"Invalid promotion piece type: {new_piece_type}. Must be 'Q', 'R', 'B', or 'N'.")
        
        # Replace the pawn with the new piece on the board
        self.board.set_piece_at(pawn_position, new_piece)
    
    def log_position(self):
        """Log the current board position for threefold repetition detection."""
        position_snapshot = self.board.get_board_snapshot()
        self.position_history.append(position_snapshot)

    def check_threefold_repetition(self):
        """Check if the current position has occurred three times."""
        current_snapshot = self.board.get_board_snapshot()
        occurrences = sum(1 for snapshot in self.position_history if snapshot == current_snapshot)
        return occurrences >= 3
    
    #check for insufficient material for checkmate
    def check_insufficient_material(self):
        """Check if the game is a draw due to insufficient material."""
        pieces = [piece for piece in self.board.board.values() if piece is not None]
        if len(pieces) == 2:
            return True  # Only kings left
        elif len(pieces) == 3:
            # One side has a king and the other has a king and a minor piece (bishop or knight)
            minor_pieces = [piece for piece in pieces if piece.type in ["B", "N"]]
            return len(minor_pieces) == 1
        elif len(pieces) == 4:
            # Both sides have only kings and bishops or knights or bishop and a knight, and both bishops are on the same color
            bishops = [piece for piece in pieces if piece.type == "B"]
            if len(bishops) == 2:
                # Check if both bishops are on the same color square
                bishop_colors = [self.board.get_square_color(piece.position) for piece in bishops]
                return bishop_colors[0] == bishop_colors[1]
            knights = [piece for piece in pieces if piece.type == "N"]
            if len(knights) == 2:
                return True  # Two knights cannot checkmate
            
        return False
    
    # SAN-Lite Builder, generates simplified SAN notation
    def generate_san_lite(self, **move_info):
        # move_info should contain:
        # "piece": piece,
        # "from": from_position,
        # "to": to_position,
        # "captured_piece": captured_piece,
        # "was_castling": was_castling,
        # "was_promotion": was_promotion,
        # "promotion_choice": promotion_choice,
        # "was_en_passant": was_en_passant,
        # "is_draw": is_draw,
        # "is_in_check": is_in_check,
        # "is_checkmate": is_checkmate
        """Generate a simplified SAN (Standard Algebraic Notation) for the move."""
        san = ""
        if move_info["was_castling"]:
            if move_info["to"][0] == 'g':
                san = "O-O"  # Kingside castling
            elif move_info["to"][0] == 'c':
                san = "O-O-O"  # Queenside castling
        else:
            if move_info["piece"].type != "P" and not move_info["was_promotion"]:
                san += move_info["piece"].type  # Add piece type for non-pawn moves
                if self._if_san_disambiguation_needed(move_info["piece"].type, move_info["to"]):
                    san += move_info["from"]  # Add disambiguation if needed
            if move_info["captured_piece"]:
                if move_info["piece"].type == "P":
                    san += move_info["from"][0]  # Add file of pawn for captures
                san += "x"  # Indicate capture
            san += move_info["to"]  # Add destination square
            if move_info["was_promotion"]:
                san += f"={move_info['promotion_choice']}"  # Indicate promotion
            if move_info["was_en_passant"]:
                san += " e.p."  # Indicate en passant capture
            if move_info["is_draw"]:
                san += " (draw)"  # Indicate draw
            if move_info["is_in_check"]:
                san += "+"  # Indicate check
            if move_info["is_checkmate"]:
                san += "#"  # Indicate checkmate
        return san

    def export_notation(self):
        """Export the move history in a simplified SAN format."""
        return [move["san"] for move in self.move_history]
    
    def load_notation(self, notation_list):
        """Load a game from a simplified SAN notation list."""
        if not isinstance(notation_list, list) or not all(isinstance(san, str) for san in notation_list):
            raise ValueError("Notation list must be a list of SAN strings.")
        
        if not notation_list:
            raise ValueError("Notation list is empty. Cannot load an empty game.")
        
        self.replay_start(notation_list)  # Start replay mode with the provided notation list

        for san in notation_list:
            self.replayer(san)  # Replay each move in the notation list
        
        self.replay_index = len(self.replay_notation)  # Set the replay index to the end after loading all moves
        self.replay_active = True  # Set replay mode to active after loading moves
            
        
    def undo_move(self):
        """Undo the last move made in the game."""
        if not self.move_history:
            raise ValueError("No moves to undo.")
        
        last_move = self.move_history.pop()  # Remove the last move from history
        self.position_history.pop()  # Remove the last position snapshot from position history
        from_position = last_move["from"]
        to_position = last_move["to"]
        piece_type = last_move["piece_type"]
        piece_color = last_move["piece_color"]
        captured_piece_type = last_move["captured_piece_type"]
        captured_piece_color = last_move["captured_piece_color"]
        was_castling = last_move["was_castling"]
        was_en_passant = last_move["was_en_passant"]
        piece_first_move_status = last_move["piece_first_move_status"]
        was_in_check = last_move["pre_move_is_in_check"] if "pre_move_is_in_check" in last_move else False
        halfmove_clock = last_move["pre_move_halfmove_clock"] if "pre_move_halfmove_clock" in last_move else 0
        was_promotion = last_move["was_promotion"] if "was_promotion" in last_move else False
        history_last_move = last_move["last_move"].copy() if last_move["last_move"] else None  # Restore the last move before the undone move
        captured_piece_has_moved = last_move["captured_piece_has_moved"] if "captured_piece_has_moved" in last_move else None

        # Restore game state variables
        self.current_turn = piece_color  # It's now the turn of the player who made the last move
        self.game_over = False  # Reset game over status
        self.last_move = history_last_move  # Restore last move before the undone move
        self.is_draw = False  # Reset draw status
        self.is_in_check = was_in_check  # Restore check status
        self.halfmove_clock = halfmove_clock  #Restore halfmove clock
        self.piece_first_move_status = piece_first_move_status  # Restore first move status for the piece
        self.draw_reason = None  # Reset draw reason

        # Restore the moved piece to its original position
        moved_piece = self.board.get_piece_at(to_position)
        if moved_piece is None or moved_piece.color != piece_color:
            raise ValueError("Inconsistent game state: Moved piece not found at expected position.")
        
        # Restore to_postition when no capture occurred
        if captured_piece_type is None:
            self.board.set_piece_at(to_position, None)  # Remove the piece from the destination square

        if not was_promotion:
            self.board.set_piece_at(from_position, moved_piece)
            moved_piece.position = from_position
            moved_piece.has_moved = piece_first_move_status  # Reset has_moved status if it's the first move of the piece
        else:
            # Handle promotion undo
            pawn_piece = Pawn(piece_color, from_position)
            pawn_piece.has_moved = True  # The pawn has moved before promotion
            self.board.set_piece_at(from_position, pawn_piece)
            self.board.set_piece_at(to_position, None)  # Remove the promoted piece from the destination square

        # Restore any captured piece to its original position
        if captured_piece_type and captured_piece_color:
            if was_en_passant:
                # For en passant, the captured pawn is behind the destination square
                captured_position = f"{to_position[0]}{from_position[1]}"
            else:
                captured_position = to_position
            
            match captured_piece_type:
                case "P":
                    captured_piece = Pawn(captured_piece_color, captured_position)
                case "R":
                    captured_piece = Rook(captured_piece_color, captured_position)
                case "N":
                    captured_piece = Knight(captured_piece_color, captured_position)   
                case "B":
                    captured_piece = Bishop(captured_piece_color, captured_position)
                case "Q":
                    captured_piece = Queen(captured_piece_color, captured_position)
                case _:
                    raise ValueError(f"Invalid captured piece type: {captured_piece_type}.")

            if captured_piece:
                captured_piece.has_moved = captured_piece_has_moved  # Restore has_moved status for the captured piece

            self.board.set_piece_at(captured_position, captured_piece)

        # Handle castling undo
        if was_castling:
            rank = '1' if piece_color == COLOR["white"] else '8'
            if to_position[0] == 'g':  # Kingside castling
                rook_from = f"h{rank}"
                rook_to = f"f{rank}"
            elif to_position[0] == 'c':  # Queenside castling
                rook_from = f"a{rank}"
                rook_to = f"d{rank}"
            else:
                raise ValueError("Invalid castling move.")

            rook = self.board.get_piece_at(rook_to)
            if rook is None or rook.type != "R" or rook.color != piece_color:
                raise ValueError("Inconsistent game state: Rook not found at expected position for castling undo.")
            
            self.board.set_piece_at(rook_from, rook)
            self.board.set_piece_at(rook_to, None)
            rook.position = rook_from
            rook.has_moved = False  # Reset has_moved status for the rook

    def _strip_san_suffixes(self, san):
        """Strip check, checkmate, and draw indicators from SAN notation."""
        e_p_flag = False
        promotion_type = None
        result = san.replace("+", "").replace("#", "").replace(" (draw)", "").strip()  # Remove check, checkmate, and draw indicators
        if "e.p." in result:
            e_p_flag = True
            result = result.replace(" e.p.", "")
        if "=" in result:
            promotion_type = result.split("=")[1]  # Extract promotion type
            result = result.split("=")[0]  # Remove promotion part for move finding
        return result, e_p_flag, promotion_type
    
    def _find_piece_for_move(self, piece_type, to_position):
        """Find the piece of the specified type that can move to the given position."""
        for from_position, piece in self.board.board.items():
            if piece and piece.type == piece_type and piece.color == self.current_turn:
                if self.rules.is_valid_move(from_position, to_position, self.last_move):
                    return from_position
        raise ValueError(f"No valid {piece_type} found that can move to {to_position}.")

    def _find_pawn_for_move(self, to_position, from_file=None):
        """Find a pawn that can legally move to the target square in current state."""
        for from_position, piece in self.board.board.items():
            if not piece:
                continue
            if piece.type != "P" or piece.color != self.current_turn:
                continue
            if from_file and from_position[0] != from_file:
                continue
            if self.rules.is_valid_move(from_position, to_position, self.last_move):
                return from_position
        raise ValueError(f"No valid pawn found that can move to {to_position}.")
    
    def _if_san_disambiguation_needed(self, piece_type, to_position):
        """Generate disambiguation for SAN notation if multiple pieces of the same type can move to the same square."""
        possible_moves = []
        for from_position, piece in self.board.board.items():
            if piece and piece.type == piece_type and piece.color == self.current_turn:
                if self.rules.is_valid_move(from_position, to_position, self.last_move):
                    possible_moves.append(from_position)
        if len(possible_moves) <= 1 or not possible_moves:
            return False
        return True
    
    def replay_start(self, notation_list):
        """Start or reset the replay of the game moves."""
        self.reset_game()  # Reset the game to the initial state
        self.replay_notation = notation_list.copy()  # Store the notation for replay purposes
        self.replay_index = 0
        self.replay_active = True

    def replay_end(self):
        """Start and reset the replay of the game at the last move."""
        if not self.replay_notation:
            return
        self.replay_start(self.replay_notation)  # Reset the game to the initial state of the replay

        for san in self.replay_notation: # Replay all moves to reach the last move
            self.replayer(san)
        
        self.replay_index = len(self.replay_notation)  # Set the replay index to the end after replaying all moves
        self.replay_active = True  # Set replay mode to active after replaying all moves

    def replay_next(self): # Replay the next move in the notation list.
        """Replay the next move in the notation list."""
        if not self.replay_active:
            raise ValueError("Replay mode is not active. Cannot replay next move.")
        if self.replay_index >= len(self.replay_notation):
            return  # Already at the end of the notation list, cannot go forward
        if not self.replay_active:
            self.replay_start(self.replay_notation)  # Reset the game to the initial state of the replay
        self.replayer(self.replay_notation[self.replay_index])  # Replay the move at the current index
        self.replay_index += 1  # Move to the next move in the replay notation

    def replay_previous(self): # Replay the previous move in the notation list.
        """Replay the previous move in the notation list."""
        if not self.replay_active:
            raise ValueError("Replay mode is not active. Cannot replay previous move.")
        if not self.replay_notation:
            return  # No replay notation loaded, cannot go back
        if self.replay_index <= 0:
            return  # Already at the beginning of the notation list, cannot go back further
        target_index = self.replay_index - 1  # Move to the previous move in the replay notation
        self.replay_start(self.replay_notation)  # Reset the game to the initial state of the replay
        for i in range(target_index):  # Replay moves up to the previous move
            self.replayer(self.replay_notation[i])
        self.replay_index = target_index  # Update the replay index to the previous move
        self.replay_active = True # Set replay mode to active after replaying the previous move

    def replayer(self, san): # Replay a single move from the notation list in SAN format.
        clean_san, e_p_flag, promotion_type = self._strip_san_suffixes(san)
        if clean_san in ["O-O", "O-O-O"]:
            # Handle castling
            rank = '1' if self.current_turn == COLOR["white"] else '8'
            from_position = f"e{rank}"
            to_position = f"g{rank}" if clean_san == "O-O" else f"c{rank}"
            self.make_move(from_position, to_position)
        else:
            # Handle normal moves
            piece_type = clean_san[0] if clean_san[0] in ["K", "Q", "R", "B", "N"] else "P"
            to_position = clean_san[-2:]  # Last two characters are the destination square
            if piece_type != "P":
                if len(clean_san) <= 4:
                    from_position = self._find_piece_for_move(piece_type, to_position)
                else:
                    from_position = clean_san[1:3]  # Disambiguation part
            else:
                capture_file = clean_san[0] if "x" in clean_san else None
                from_position = self._find_pawn_for_move(to_position, capture_file)
            self.make_move(from_position, to_position, promotion_choice=promotion_type if promotion_type else "Q")

    def get_legal_moves(self, position):
        """Get all legal moves for the piece at the specified position."""
        piece = self.board.get_piece_at(position)
        if not piece:
            raise ValueError(f"No piece at position {position}.")
        
        legal_moves = []
        for to_position in self.board.board.keys():
            if self.rules.is_valid_move(position, to_position, self.last_move):
                if not self.would_be_in_check_after_move(position, to_position):
                    legal_moves.append(to_position)
        if piece.type == "K":
            rank = "1" if piece.color == COLOR["white"] else "8"
            if position == f"e{rank}":
                if self.can_castle(piece.color, "kingside"):
                    legal_moves.append(f"g{rank}")
                if self.can_castle(piece.color, "queenside"):
                    legal_moves.append(f"c{rank}")

        return legal_moves
