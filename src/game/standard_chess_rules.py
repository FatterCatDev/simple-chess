from game.board import ChessBoard
from utils.constants import FILES, RANKS, COLOR

class StandardChessRules:
    def __init__(self, chess_board: ChessBoard):
        self.board = chess_board

    def is_valid_move(self, from_position, to_position):
        """Check if a move from one position to another is valid according to standard chess rules."""
        move_valid = False
        piece = self.board.get_piece_at(from_position)
        if piece is None or from_position == to_position:
            return False
        
        # Implement specific movement rules for each piece type
        match piece.type:
            case "P":
                if self.is_valid_pawn_move(piece, from_position, to_position):
                    move_valid = True
            case "R":
                if self.is_valid_rook_move(piece, from_position, to_position):
                    move_valid = True
            case "N":
                if self.is_valid_knight_move(piece, from_position, to_position):
                    move_valid = True
            case "B":
                if self.is_valid_bishop_move(piece, from_position, to_position):
                    move_valid = True
            case "Q":
                if self.is_valid_queen_move(piece, from_position, to_position):
                    move_valid = True
            case "K":
                if self.is_valid_king_move(piece, from_position, to_position):
                    move_valid = True
            case _:
                raise ValueError(f"Unknown piece type: {piece.type}")
            
        if self.board.is_position_occupied(to_position) and self.board.get_piece_at(to_position).color == piece.color:
            move_valid = False  # Cannot capture own piece
        return move_valid
    
    # Placeholder methods for specific piece movement rules
    def is_valid_pawn_move(self, pawn, from_position, to_position):
        if from_position[0] == to_position[0]:  # Same file
            if pawn.color == COLOR["white"] and self.board.get_piece_at(to_position) is None:
                if from_position[1] == '2' and to_position[1] == '4' and self.board.get_piece_at(f"{from_position[0]}3") is None:
                    return True  # Initial two-square move
                elif int(to_position[1]) - int(from_position[1]) == 1:
                    return True  # Normal one-square move
            elif pawn.color == COLOR["black"] and self.board.get_piece_at(to_position) is None:
                if from_position[1] == '7' and to_position[1] == '5' and self.board.get_piece_at(f"{from_position[0]}6") is None:
                    return True  # Initial two-square move
                elif int(from_position[1]) - int(to_position[1]) == 1:
                    return True  # Normal one-square move
        elif abs(ord(from_position[0]) - ord(to_position[0])) == 1:  # Diagonal capture
            if pawn.color == COLOR["white"] and int(to_position[1]) - int(from_position[1]) == 1:
                if self.board.is_position_occupied(to_position) and self.board.get_piece_at(to_position).color == COLOR["black"]:
                        return True  # Capture move
                # en passant capture for white pawns
            elif pawn.color == COLOR["black"] and int(from_position[1]) - int(to_position[1]) == 1:
                if self.board.is_position_occupied(to_position) and self.board.get_piece_at(to_position).color == COLOR["white"]:
                    return True  # Capture move
                # en passant capture for black pawns
        return False

    def is_valid_rook_move(self, rook, from_position, to_position):
        if from_position[0] == to_position[0] or from_position[1] == to_position[1]:  # Same file or rank
            if self.line_diagonal_clear(from_position, to_position):
                return True
        return False

    def is_valid_knight_move(self, knight, from_position, to_position):
        from_position_index = self.algebraic_to_coordinate(from_position)
        to_position_index = self.algebraic_to_coordinate(to_position)
        file_diff = to_position_index[0] - from_position_index[0]
        rank_diff = to_position_index[1] - from_position_index[1]
        if (file_diff, rank_diff) in [  (2, 1), 
                                        (2, -1), 
                                        (-2, 1), 
                                        (-2, -1), 
                                        (1, 2), 
                                        (1, -2), 
                                        (-1, 2), 
                                        (-1, -2)]:
            if not self.board.is_position_occupied(to_position) or self.board.get_piece_at(to_position).color != knight.color:
                return True
        return False

    def is_valid_bishop_move(self, bishop, from_position, to_position):
        from_coord = self.algebraic_to_coordinate(from_position)
        to_coord = self.algebraic_to_coordinate(to_position)
        if abs(from_coord[0] - to_coord[0]) == abs(from_coord[1] - to_coord[1]):  # Diagonal move
            if self.line_diagonal_clear(from_position, to_position):
                return True
        return False

    def is_valid_queen_move(self, queen, from_position, to_position):
        # Queen can move like a rook or a bishop
        return self.is_valid_rook_move(queen, from_position, to_position) or self.is_valid_bishop_move(queen, from_position, to_position)

    def is_valid_king_move(self, king, from_position, to_position):
        # Implement king movement logic here
        from_coord = self.algebraic_to_coordinate(from_position)
        to_coord = self.algebraic_to_coordinate(to_position)
        if max(abs(from_coord[0] - to_coord[0]), abs(from_coord[1] - to_coord[1])) == 1:
            if not self.board.is_position_occupied(to_position) or self.board.get_piece_at(to_position).color != king.color:
                return True
        return False

    def algebraic_to_coordinate(self, algebraic):
        """Convert algebraic notation (e.g., 'e4') to board coordinates (e.g., (4, 3))."""
        file = ord(algebraic[0]) - ord('a')
        rank = int(algebraic[1]) - 1
        return (file, rank)
    
    def line_diagonal_clear(self, from_position, to_position):
        """Check if the path between two positions is clear for linear or diagonal movement."""
        from_file, from_rank = self.algebraic_to_coordinate(from_position)
        to_file, to_rank = self.algebraic_to_coordinate(to_position)

        file_step = 1 if to_file > from_file else -1 if to_file < from_file else 0
        rank_step = 1 if to_rank > from_rank else -1 if to_rank < from_rank else 0

        current_file = from_file + file_step
        current_rank = from_rank + rank_step

        while (current_file, current_rank) != (to_file, to_rank):
            position = f"{chr(current_file + ord('a'))}{current_rank + 1}"
            if self.board.is_position_occupied(position):
                return False
            current_file += file_step
            current_rank += rank_step

        return True
    
    def is_valid_pawn_attack(self, pawn, from_position, to_position):
        """Check if a pawn can attack a specific position."""
        from_file, from_rank = self.algebraic_to_coordinate(from_position)
        to_file, to_rank = self.algebraic_to_coordinate(to_position)

        if pawn.color == COLOR["white"]:
            return (to_rank - from_rank == 1) and (abs(to_file - from_file) == 1)
        else:  # black pawn
            return (from_rank - to_rank == 1) and (abs(to_file - from_file) == 1)