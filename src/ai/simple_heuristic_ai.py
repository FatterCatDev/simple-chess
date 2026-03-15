import random
from ai.ai import AIEngine
from utils.constants import PIECE_VALUES, FILES, RANKS

class SimpleHeuristicAI(AIEngine):
    """A simple heuristic-based AI engine for chess."""

    def __init__(self, difficulty=1):
        super().__init__()
        self.name = f"Simple Heuristic AI | ELO: {difficulty * 100}"
        self.difficulty = difficulty  # Difficulty can be used to adjust the depth of move evaluation

    def get_move(self, game):
        all_moves = self._collect_all_moves(game)
        if not all_moves:
            return None  # No valid moves available
        if self.difficulty == 1:
            return self._best_greedy_move(game)
        elif self.difficulty >= 2:
            return self._best_lookahead_move(game, all_moves)

    def _collect_all_moves(self, game):
        """Collect all legal moves for the current player."""
        all_moves = []
        for square in game.board.board:
            if not isinstance(square, str) or len(square) != 2 or square[0] not in FILES or square[1] not in RANKS:
                continue  # Skip invalid squares
            piece = game.board.get_piece_at(square)
            if piece and piece.color == game.current_turn:
                for target_square in game.get_legal_moves(square):
                    all_moves.append((square, target_square))
        return all_moves

    def _evaluate_move(self, game, from_square, to_square):
        """Evaluate a move based on simple heuristics."""
        piece = game.board.get_piece_at(from_square)
        target_piece = game.board.get_piece_at(to_square)

        # Basic heuristic: prioritize capturing higher-value pieces
        score = 0
        if target_piece and target_piece.color != piece.color:
            score += PIECE_VALUES[target_piece.type]  # Add value of captured piece
        
        if game.is_square_under_attack(to_square, game.opponent_color()):
            score -= PIECE_VALUES[piece.type]  # Penalize if moving to a square under attack


        # Additional heuristics can be added here (e.g., controlling the center, king safety, etc.)

        return score
    
    def _best_greedy_move(self, game):
        """Select the best move based on the heuristic evaluation."""
        all_moves = self._collect_all_moves(game)
        best_moves = []
        best_score = float('-inf')

        for from_square, to_square in all_moves:
            score = self._evaluate_move(game, from_square, to_square)

            if score > best_score:
                best_score = score
                best_moves = []
                best_moves.append((from_square, to_square))
            elif score == best_score:
                # Randomly choose between moves with the same score to add variability
                best_moves.append((from_square, to_square))

        if not best_moves:
            raise ValueError("No valid moves available for the current player.")

        return random.choice(best_moves)
    
    def _best_lookahead_move(self, game, moves):
        """Select the best move based on a lookahead evaluation."""
        best_moves = []
        best_score = float('-inf')

        for from_square, to_square in moves:
            immediate = self._evaluate_move(game, from_square, to_square)

            game.make_move(from_square, to_square)
            if game.game_over:
                is_winning_move = not game.is_draw
                game.undo_move()

                if is_winning_move:
                    return (from_square, to_square)

                lookahead = immediate
                if lookahead > best_score:
                    best_score = lookahead
                    best_moves = [(from_square, to_square)]
                elif lookahead == best_score:
                    best_moves.append((from_square, to_square))

                continue

            check_bonus = 0.5 if game.is_in_check else 0
            opponent_moves = self._collect_all_moves(game)
            opponent_best_score = float('-inf')

            for opponent_move in opponent_moves:
                if not isinstance(opponent_move, tuple) or len(opponent_move) != 2:
                    continue
                opp_from, opp_to = opponent_move
                opp_score = self._evaluate_move(game, opp_from, opp_to)
                if opp_score > opponent_best_score:
                    opponent_best_score = opp_score

            if opponent_best_score == float('-inf'):
                opponent_best_score = 0

            lookahead = immediate - opponent_best_score + check_bonus
            game.undo_move()

            if lookahead > best_score:
                best_score = lookahead
                best_moves = [(from_square, to_square)]
            elif lookahead == best_score:
                best_moves.append((from_square, to_square))

        if not best_moves:
            raise ValueError("No valid moves available for the current player.")

        return random.choice(best_moves)