from ai.sim_state import AIState, LastMoveState, PieceState
from game.game import Game
from game.piece import Bishop, King, Knight, Pawn, Queen, Rook
from utils.constants import FILES, RANKS


PIECE_TYPES = {
    "P": Pawn,
    "N": Knight,
    "B": Bishop,
    "R": Rook,
    "Q": Queen,
    "K": King,
}


def build_piece_map(state):
    return {piece.position: piece for piece in state.pieces}


def get_piece_at_state(state, square, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)
    return piece_map.get(square)


def _square_to_coords(square):
    return FILES.index(square[0]), RANKS.index(square[1])


def _coords_to_square(file_index, rank_index):
    if 0 <= file_index < 8 and 0 <= rank_index < 8:
        return f"{FILES[file_index]}{RANKS[rank_index]}"
    return None


def is_square_under_attack_state(state, square, attacking_color, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)

    target_file, target_rank = _square_to_coords(square)

    for piece in piece_map.values():
        if piece.color != attacking_color:
            continue

        piece_file, piece_rank = _square_to_coords(piece.position)
        file_delta = target_file - piece_file
        rank_delta = target_rank - piece_rank

        if piece.piece_type == "P":
            direction = 1 if piece.color == "W" else -1
            if rank_delta == direction and abs(file_delta) == 1:
                return True
        elif piece.piece_type == "N":
            if (abs(file_delta), abs(rank_delta)) in {(1, 2), (2, 1)}:
                return True
        elif piece.piece_type == "K":
            if max(abs(file_delta), abs(rank_delta)) == 1:
                return True
        elif piece.piece_type in {"B", "R", "Q"}:
            directions = []
            if piece.piece_type in {"B", "Q"} and abs(file_delta) == abs(rank_delta) and file_delta != 0:
                directions.append((1 if file_delta > 0 else -1, 1 if rank_delta > 0 else -1))
            if piece.piece_type in {"R", "Q"}:
                if file_delta == 0 and rank_delta != 0:
                    directions.append((0, 1 if rank_delta > 0 else -1))
                elif rank_delta == 0 and file_delta != 0:
                    directions.append((1 if file_delta > 0 else -1, 0))

            for file_step, rank_step in directions:
                current_file = piece_file + file_step
                current_rank = piece_rank + rank_step

                while 0 <= current_file < 8 and 0 <= current_rank < 8:
                    current_square = _coords_to_square(current_file, current_rank)
                    if current_square == square:
                        return True
                    if current_square in piece_map:
                        break
                    current_file += file_step
                    current_rank += rank_step

    return False


def _serialize_last_move(last_move):
    if not last_move:
        return None
    return LastMoveState(
        from_square=last_move["from"],
        to_square=last_move["to"],
        was_two_square_pawn_move=last_move["was_two_square_pawn_move"],
    )


def _deserialize_last_move(last_move_state):
    if not last_move_state:
        return None
    return {
        "from": last_move_state.from_square,
        "to": last_move_state.to_square,
        "was_two_square_pawn_move": last_move_state.was_two_square_pawn_move,
    }


def _serialize_position_history(position_history):
    serialized = []
    for snapshot in position_history:
        serialized.append(tuple((square, snapshot.get(square)) for square in sorted(snapshot.keys())))
    return tuple(serialized)


def _deserialize_position_history(position_history):
    return [dict(snapshot) for snapshot in position_history]


def game_to_ai_state(game):
    """Capture the minimum immutable game data needed for AI simulation."""
    pieces = []
    for square in (f"{file}{rank}" for rank in RANKS for file in FILES):
        piece = game.board.get_piece_at(square)
        if piece is None:
            continue
        pieces.append(PieceState(square, piece.color, piece.type, piece.has_moved))

    return AIState(
        pieces=tuple(pieces),
        current_turn=game.current_turn,
        game_over=game.game_over,
        is_draw=game.is_draw,
        draw_reason=game.draw_reason,
        halfmove_clock=game.halfmove_clock,
        is_in_check=game.is_in_check,
        last_move=_serialize_last_move(game.last_move),
        position_history=_serialize_position_history(game.position_history),
        enable_fifty_move_rule=game.enable_fifty_move_rule,
    )


def ai_state_to_game(state):
    """Rebuild a lightweight Game instance from immutable AIState."""
    simulated_game = Game(enable_fifty_move_rule=state.enable_fifty_move_rule)

    for square in (f"{file}{rank}" for rank in RANKS for file in FILES):
        simulated_game.board.remove_piece_at(square)

    for piece_state in state.pieces:
        piece = PIECE_TYPES[piece_state.piece_type](piece_state.color, piece_state.position)
        piece.has_moved = piece_state.has_moved
        simulated_game.board.set_piece_at(piece_state.position, piece)

    simulated_game.current_turn = state.current_turn
    simulated_game.game_over = state.game_over
    simulated_game.is_draw = state.is_draw
    simulated_game.draw_reason = state.draw_reason
    simulated_game.halfmove_clock = state.halfmove_clock
    simulated_game.is_in_check = state.is_in_check
    simulated_game.last_move = _deserialize_last_move(state.last_move)
    simulated_game.position_history = _deserialize_position_history(state.position_history)
    simulated_game.move_history = []

    return simulated_game


def apply_move_on_state(state, from_square, to_square, promotion_choice="Q"):
    """Apply a move to an immutable AIState and return the next AIState."""
    simulated_game = ai_state_to_game(state)
    simulated_game.make_move(from_square, to_square, promotion_choice=promotion_choice)
    return game_to_ai_state(simulated_game)
