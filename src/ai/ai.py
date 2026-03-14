import random

class AIEngine:
    def get_move(self, game):
        """Return a move based on the current game state. This method should be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses.")

class RandomAI(AIEngine):
    def __init__(self):
        self.name = "Random AI | ELO: 0"
    def get_move(self, game):
        """Generate a random valid move"""
        all_moves = []
        for square in game.board.board:
            piece = game.board.get_piece_at(square)
            if piece and piece.color == game.current_turn:
                for target_square in game.get_legal_moves(square):
                    all_moves.append((square, target_square))
        if not all_moves:
            return None  # No valid moves available
        return random.choice(all_moves)