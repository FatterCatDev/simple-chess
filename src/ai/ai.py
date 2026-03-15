import random

class AIEngine:
    def get_move(self, game):
        """Return a move based on the current game state. This method should be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses.")

class RandomAI(AIEngine):
    def __init__(self):
        self.engine_name = "Random AI"
        self.difficulty = 0
        self.name = "Random AI | ELO: 0"
    def get_move(self, game):
        """Generate a random valid move"""
        all_moves = game.get_all_valid_moves(game.current_turn)
        if not all_moves:
            return None  # No valid moves available
        return random.choice(all_moves)