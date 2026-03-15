import random
from collections import OrderedDict
from ai.ai import AIEngine
from ai.sim_adapter import (
    apply_move_on_state,
    generate_legal_moves_on_state,
    game_to_ai_state,
    get_piece_at_state,
    is_in_check_state,
    is_square_under_attack_state,
)
from utils.constants import PIECE_VALUES

class SimpleHeuristicAI(AIEngine):
    """A simple heuristic-based AI engine for chess."""

    MAX_CANDIDATE_MOVES = 24
    MAX_REPLY_MOVES = 24
    MAX_TRANSPOSITION_ENTRIES = 2048

    def __init__(self, difficulty=1):
        super().__init__()
        self.engine_name = "Simple Heuristic AI"
        self.name = f"Simple Heuristic AI | ELO: {difficulty * 100}"
        self.difficulty = difficulty  # Difficulty can be used to adjust the depth of move evaluation
        self._legal_moves_cache = OrderedDict()
        self._in_check_cache = OrderedDict()
        self._opponent_reply_cache = OrderedDict()

    def _cache_set(self, cache, key, value):
        cache[key] = value
        cache.move_to_end(key)
        if len(cache) > self.MAX_TRANSPOSITION_ENTRIES:
            cache.popitem(last=False)

    def _state_cache_key(self, state):
        return (
            state.pieces,
            state.current_turn,
            state.last_move,
            state.enable_fifty_move_rule,
        )

    def _cached_legal_moves(self, state):
        key = self._state_cache_key(state)
        if key in self._legal_moves_cache:
            self._legal_moves_cache.move_to_end(key)
            return self._legal_moves_cache[key]
        moves = generate_legal_moves_on_state(state)
        self._cache_set(self._legal_moves_cache, key, moves)
        return moves

    def _cached_in_check(self, state, color):
        key = (self._state_cache_key(state), color)
        if key in self._in_check_cache:
            self._in_check_cache.move_to_end(key)
            return self._in_check_cache[key]
        in_check = is_in_check_state(state, color)
        self._cache_set(self._in_check_cache, key, in_check)
        return in_check

    def get_move(self, game):
        all_moves = game.get_all_valid_moves(game.current_turn)
        if not all_moves:
            return None  # No valid moves available
        if self.difficulty == 1:
            return self._best_greedy_move(game)
        elif self.difficulty >= 2:
            return self._best_lookahead_move(game, all_moves)

    def _evaluate_move(self, game, from_square, to_square):
        """Evaluate a move based on simple heuristics."""
        piece = game.board.get_piece_at(from_square)
        target_piece = game.board.get_piece_at(to_square)

        if piece is None:
            return float('-inf')

        # Basic heuristic: prioritize capturing higher-value pieces
        score = 0
        if target_piece and target_piece.color != piece.color:
            score += PIECE_VALUES[target_piece.type]  # Add value of captured piece
        
        if game.is_square_under_attack(to_square, game.opponent_color()):
            score -= PIECE_VALUES[piece.type]  # Penalize if moving to a square under attack


        # Additional heuristics can be added here (e.g., controlling the center, king safety, etc.)

        return score

    def _evaluate_move_on_state(self, state, from_square, to_square):
        piece = get_piece_at_state(state, from_square)
        target_piece = get_piece_at_state(state, to_square)

        if piece is None:
            return float('-inf')

        score = 0
        if target_piece and target_piece.color != piece.color:
            score += PIECE_VALUES[target_piece.piece_type]

        opponent_color = "B" if piece.color == "W" else "W"
        if is_square_under_attack_state(state, to_square, opponent_color):
            score -= PIECE_VALUES[piece.piece_type]

        return score
    
    def _best_greedy_move(self, game):
        """Select the best move based on the heuristic evaluation."""
        all_moves = game.get_all_valid_moves(game.current_turn)
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

    def _top_scored_moves(self, game, moves, limit):
        """Return top-N moves ordered by immediate heuristic score."""
        scored_moves = []
        for move in moves:
            if not isinstance(move, tuple) or len(move) != 2:
                continue
            from_square, to_square = move
            scored_moves.append((self._evaluate_move(game, from_square, to_square), move))

        scored_moves.sort(key=lambda item: item[0], reverse=True)
        return [move for _, move in scored_moves[:limit]]

    def _top_scored_state_moves(self, state, moves, limit):
        scored_moves = []
        for move in moves:
            if not isinstance(move, tuple) or len(move) != 2:
                continue
            from_square, to_square = move
            scored_moves.append((self._evaluate_move_on_state(state, from_square, to_square), move))

        scored_moves.sort(key=lambda item: item[0], reverse=True)
        return [move for _, move in scored_moves[:limit]]

    def _cached_opponent_best_reply_score(self, state):
        key = self._state_cache_key(state)
        if key in self._opponent_reply_cache:
            self._opponent_reply_cache.move_to_end(key)
            return self._opponent_reply_cache[key]

        opponent_moves = self._cached_legal_moves(state)
        opponent_moves = self._top_scored_state_moves(state, opponent_moves, self.MAX_REPLY_MOVES)
        opponent_best_score = float('-inf')

        for opponent_move in opponent_moves:
            if not isinstance(opponent_move, tuple) or len(opponent_move) != 2:
                continue
            opp_from, opp_to = opponent_move
            opp_score = self._evaluate_move_on_state(state, opp_from, opp_to)
            if opp_score > opponent_best_score:
                opponent_best_score = opp_score

        if opponent_best_score == float('-inf'):
            opponent_best_score = 0

        self._cache_set(self._opponent_reply_cache, key, opponent_best_score)
        return opponent_best_score
    
    def _best_lookahead_move(self, game, moves):
        """Select the best move based on a lookahead evaluation."""
        self._legal_moves_cache.clear()
        self._in_check_cache.clear()
        self._opponent_reply_cache.clear()

        best_moves = []
        best_score = float('-inf')
        root_state = game_to_ai_state(game)

        for from_square, to_square in moves:
            winning_state = apply_move_on_state(root_state, from_square, to_square)
            opponent_moves = self._cached_legal_moves(winning_state)
            if not opponent_moves and self._cached_in_check(winning_state, winning_state.current_turn):
                return (from_square, to_square)

        candidate_moves = self._top_scored_state_moves(root_state, moves, self.MAX_CANDIDATE_MOVES)

        for from_square, to_square in candidate_moves:
            immediate = self._evaluate_move_on_state(root_state, from_square, to_square)
            simulated_state = apply_move_on_state(root_state, from_square, to_square)
            opponent_moves = self._cached_legal_moves(simulated_state)

            if not opponent_moves:
                if self._cached_in_check(simulated_state, simulated_state.current_turn):
                    return (from_square, to_square)
                lookahead = immediate
            else:
                check_bonus = 0.5 if simulated_state.is_in_check else 0
                opponent_best_score = self._cached_opponent_best_reply_score(simulated_state)

                lookahead = immediate - opponent_best_score + check_bonus

            if lookahead > best_score:
                best_score = lookahead
                best_moves = [(from_square, to_square)]
            elif lookahead == best_score:
                best_moves.append((from_square, to_square))

        if not best_moves:
            raise ValueError("No valid moves available for the current player.")
        return random.choice(best_moves)