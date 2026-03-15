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


def opponent_color(color):
    return "B" if color == "W" else "W"


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


def _line_clear_state(from_square, to_square, piece_map):
    from_file, from_rank = _square_to_coords(from_square)
    to_file, to_rank = _square_to_coords(to_square)

    file_step = 1 if to_file > from_file else -1 if to_file < from_file else 0
    rank_step = 1 if to_rank > from_rank else -1 if to_rank < from_rank else 0

    current_file = from_file + file_step
    current_rank = from_rank + rank_step

    while (current_file, current_rank) != (to_file, to_rank):
        current_square = _coords_to_square(current_file, current_rank)
        if current_square in piece_map:
            return False
        current_file += file_step
        current_rank += rank_step

    return True


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


def is_en_passant_possible_state(state, pawn_position, to_position):
    last_move = state.last_move
    if not last_move or not last_move.was_two_square_pawn_move:
        return False

    pawn_file = pawn_position[0]
    pawn_rank = int(pawn_position[1])
    last_move_file = last_move.to_square[0]
    last_move_rank = int(last_move.to_square[1])
    to_file = to_position[0]
    to_rank = int(to_position[1])

    if last_move_rank == pawn_rank and abs(ord(last_move_file) - ord(pawn_file)) == 1:
        if to_file == last_move_file and ((pawn_rank == 5 and to_rank == 6) or (pawn_rank == 4 and to_rank == 3)):
            return True

    return False


def is_valid_state_move(state, from_square, to_square, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)

    piece = piece_map.get(from_square)
    if piece is None or from_square == to_square:
        return False

    target_piece = piece_map.get(to_square)
    if target_piece and target_piece.color == piece.color:
        return False

    from_file, from_rank = _square_to_coords(from_square)
    to_file, to_rank = _square_to_coords(to_square)
    file_diff = to_file - from_file
    rank_diff = to_rank - from_rank

    if piece.piece_type == "P":
        direction = 1 if piece.color == "W" else -1
        start_rank = 1 if piece.color == "W" else 6

        if from_file == to_file and target_piece is None:
            if rank_diff == direction:
                return True
            if from_rank == start_rank and rank_diff == 2 * direction:
                middle_square = _coords_to_square(from_file, from_rank + direction)
                return middle_square not in piece_map

        if abs(file_diff) == 1 and rank_diff == direction:
            if target_piece and target_piece.color != piece.color:
                return True
            if target_piece is None and is_en_passant_possible_state(state, from_square, to_square):
                return True
        return False

    if piece.piece_type == "N":
        return (abs(file_diff), abs(rank_diff)) in {(1, 2), (2, 1)}

    if piece.piece_type == "B":
        return abs(file_diff) == abs(rank_diff) and file_diff != 0 and _line_clear_state(from_square, to_square, piece_map)

    if piece.piece_type == "R":
        return (file_diff == 0 or rank_diff == 0) and (file_diff != 0 or rank_diff != 0) and _line_clear_state(from_square, to_square, piece_map)

    if piece.piece_type == "Q":
        diagonal = abs(file_diff) == abs(rank_diff) and file_diff != 0
        straight = (file_diff == 0 or rank_diff == 0) and (file_diff != 0 or rank_diff != 0)
        return (diagonal or straight) and _line_clear_state(from_square, to_square, piece_map)

    if piece.piece_type == "K":
        return max(abs(file_diff), abs(rank_diff)) == 1

    return False


def find_king_state(state, color, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)
    for piece in piece_map.values():
        if piece.color == color and piece.piece_type == "K":
            return piece.position
    raise ValueError(f"No king found for color {color}.")


def is_in_check_state(state, color, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)
    king_position = find_king_state(state, color, piece_map)
    return is_square_under_attack_state(state, king_position, opponent_color(color), piece_map)


def can_castle_state(state, color, side, piece_map=None):
    if piece_map is None:
        piece_map = build_piece_map(state)

    if is_in_check_state(state, color, piece_map):
        return False

    rank = "1" if color == "W" else "8"
    king_position = f"e{rank}"
    rook_position = f"h{rank}" if side == "kingside" else f"a{rank}"
    king = piece_map.get(king_position)
    rook = piece_map.get(rook_position)

    if not king or not rook:
        return False
    if king.piece_type != "K" or rook.piece_type != "R":
        return False
    if king.color != color or rook.color != color:
        return False
    if king.has_moved or rook.has_moved:
        return False

    files_between = ["f", "g"] if side == "kingside" else ["b", "c", "d"]
    for file in files_between:
        if f"{file}{rank}" in piece_map:
            return False

    king_path = [f"e{rank}", f"f{rank}", f"g{rank}"] if side == "kingside" else [f"e{rank}", f"d{rank}", f"c{rank}"]
    for square in king_path:
        if is_square_under_attack_state(state, square, opponent_color(color), piece_map):
            return False

    return True


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


def _build_position_snapshot_from_piece_map(piece_map):
    snapshot = []
    for square in sorted(f"{file}{rank}" for rank in RANKS for file in FILES):
        piece = piece_map.get(square)
        snapshot.append((square, None if piece is None else (piece.piece_type, piece.color)))
    return tuple(snapshot)


def apply_move_on_state(state, from_square, to_square, promotion_choice="Q"):
    """Apply a move to an immutable AIState and return the next AIState."""
    piece_map = build_piece_map(state)
    piece = piece_map.get(from_square)
    if piece is None:
        raise ValueError(f"No piece at position {from_square} to move.")

    new_map = dict(piece_map)
    captured_piece = new_map.get(to_square)
    is_castle = piece.piece_type == "K" and abs(ord(from_square[0]) - ord(to_square[0])) == 2 and from_square[1] == to_square[1]
    is_en_passant = (
        piece.piece_type == "P"
        and captured_piece is None
        and from_square[0] != to_square[0]
        and is_en_passant_possible_state(state, from_square, to_square)
    )

    new_map.pop(from_square, None)
    if captured_piece is not None:
        new_map.pop(to_square, None)

    if is_en_passant:
        captured_pawn_square = f"{to_square[0]}{from_square[1]}"
        new_map.pop(captured_pawn_square, None)

    if is_castle:
        rank = from_square[1]
        if to_square[0] == "g":
            rook_from = f"h{rank}"
            rook_to = f"f{rank}"
        else:
            rook_from = f"a{rank}"
            rook_to = f"d{rank}"
        rook = new_map.pop(rook_from)
        new_map[rook_to] = PieceState(rook_to, rook.color, rook.piece_type, True)

    next_piece_type = piece.piece_type
    if piece.piece_type == "P":
        promotion_rank = "8" if piece.color == "W" else "1"
        if to_square[1] == promotion_rank:
            next_piece_type = promotion_choice

    new_map[to_square] = PieceState(to_square, piece.color, next_piece_type, True)

    next_last_move = LastMoveState(
        from_square=from_square,
        to_square=to_square,
        was_two_square_pawn_move=piece.piece_type == "P" and abs(int(from_square[1]) - int(to_square[1])) == 2,
    )
    next_turn = opponent_color(state.current_turn)
    next_halfmove = 0 if piece.piece_type == "P" or captured_piece is not None or is_en_passant else state.halfmove_clock + 1

    next_state = AIState(
        pieces=tuple(sorted(new_map.values(), key=lambda item: item.position)),
        current_turn=next_turn,
        game_over=False,
        is_draw=False,
        draw_reason=None,
        halfmove_clock=next_halfmove,
        is_in_check=False,
        last_move=next_last_move,
        position_history=state.position_history + (_build_position_snapshot_from_piece_map(new_map),),
        enable_fifty_move_rule=state.enable_fifty_move_rule,
    )

    return AIState(
        pieces=next_state.pieces,
        current_turn=next_state.current_turn,
        game_over=False,
        is_draw=False,
        draw_reason=None,
        halfmove_clock=next_state.halfmove_clock,
        is_in_check=is_in_check_state(next_state, next_turn),
        last_move=next_state.last_move,
        position_history=next_state.position_history,
        enable_fifty_move_rule=next_state.enable_fifty_move_rule,
    )


def would_be_in_check_after_state_move(state, from_square, to_square):
    next_state = apply_move_on_state(state, from_square, to_square)
    return is_in_check_state(next_state, state.current_turn)


def _generate_pseudo_targets_for_piece(state, piece, piece_map):
    targets = []
    from_square = piece.position
    from_file, from_rank = _square_to_coords(from_square)

    def add_target_if_enemy_or_empty(file_index, rank_index):
        square = _coords_to_square(file_index, rank_index)
        if square is None:
            return
        target_piece = piece_map.get(square)
        if target_piece is None or target_piece.color != piece.color:
            targets.append(square)

    if piece.piece_type == "P":
        direction = 1 if piece.color == "W" else -1
        start_rank = 1 if piece.color == "W" else 6

        one_step = _coords_to_square(from_file, from_rank + direction)
        if one_step and one_step not in piece_map:
            targets.append(one_step)
            two_step = _coords_to_square(from_file, from_rank + (2 * direction))
            if from_rank == start_rank and two_step and two_step not in piece_map:
                targets.append(two_step)

        for file_step in (-1, 1):
            capture_square = _coords_to_square(from_file + file_step, from_rank + direction)
            if capture_square is None:
                continue
            target_piece = piece_map.get(capture_square)
            if target_piece and target_piece.color != piece.color:
                targets.append(capture_square)
            elif is_en_passant_possible_state(state, from_square, capture_square):
                targets.append(capture_square)

        return targets

    if piece.piece_type == "N":
        for file_step, rank_step in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            add_target_if_enemy_or_empty(from_file + file_step, from_rank + rank_step)
        return targets

    if piece.piece_type == "K":
        for file_step in (-1, 0, 1):
            for rank_step in (-1, 0, 1):
                if file_step == 0 and rank_step == 0:
                    continue
                add_target_if_enemy_or_empty(from_file + file_step, from_rank + rank_step)
        return targets

    directions = []
    if piece.piece_type in {"B", "Q"}:
        directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    if piece.piece_type in {"R", "Q"}:
        directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])

    for file_step, rank_step in directions:
        current_file = from_file + file_step
        current_rank = from_rank + rank_step

        while 0 <= current_file < 8 and 0 <= current_rank < 8:
            square = _coords_to_square(current_file, current_rank)
            target_piece = piece_map.get(square)

            if target_piece is None:
                targets.append(square)
            else:
                if target_piece.color != piece.color:
                    targets.append(square)
                break

            current_file += file_step
            current_rank += rank_step

    return targets


def generate_legal_moves_on_state(state):
    piece_map = build_piece_map(state)
    legal_moves = []

    for piece in state.pieces:
        if piece.color != state.current_turn:
            continue

        for to_square in _generate_pseudo_targets_for_piece(state, piece, piece_map):
            if not would_be_in_check_after_state_move(state, piece.position, to_square):
                legal_moves.append((piece.position, to_square))

        if piece.piece_type == "K":
            rank = "1" if piece.color == "W" else "8"
            if piece.position == f"e{rank}":
                if can_castle_state(state, piece.color, "kingside", piece_map):
                    legal_moves.append((piece.position, f"g{rank}"))
                if can_castle_state(state, piece.color, "queenside", piece_map):
                    legal_moves.append((piece.position, f"c{rank}"))

    return legal_moves
