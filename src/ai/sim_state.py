from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class PieceState:
    position: str
    color: str
    piece_type: str
    has_moved: bool


@dataclass(frozen=True)
class LastMoveState:
    from_square: str
    to_square: str
    was_two_square_pawn_move: bool


@dataclass(frozen=True)
class AIState:
    pieces: Tuple[PieceState, ...]
    current_turn: str
    game_over: bool
    is_draw: bool
    draw_reason: Optional[str]
    halfmove_clock: int
    is_in_check: bool
    last_move: Optional[LastMoveState]
    position_history: Tuple[Tuple[Tuple[str, Optional[Tuple[str, str]]], ...], ...]
    enable_fifty_move_rule: bool
