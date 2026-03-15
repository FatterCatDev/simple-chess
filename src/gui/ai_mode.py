from ai.ai import RandomAI
from ai.simple_heuristic_ai import SimpleHeuristicAI
from gui.controller import GameController

ENGINE_OPTIONS = [
    ("Random AI", lambda: RandomAI()),
    ("Simple Heuristic AI (Easy)", lambda: SimpleHeuristicAI(difficulty=1)),
    ("Simple Heuristic AI (Hard)", lambda: SimpleHeuristicAI(difficulty=2)),
]


def ai_meta_from_engine(ai_engine):
    if ai_engine is None:
        return None
    return {
        "engine": getattr(ai_engine, "engine_name", None) or "Random AI",
        "difficulty": getattr(ai_engine, "difficulty", 0),
    }


def build_controller_for_mode(
    game_instance,
    mode_key,
    player_color="W",
    chosen_engine=None,
    chosen_white_engine=None,
    chosen_black_engine=None,
):
    engine_lookup = dict(ENGINE_OPTIONS)

    if mode_key == "aivai":
        engine_factory_white = engine_lookup.get(chosen_white_engine) if chosen_white_engine else None
        engine_factory_black = engine_lookup.get(chosen_black_engine) if chosen_black_engine else None
        ai_white = engine_factory_white() if engine_factory_white else RandomAI()
        ai_black = engine_factory_black() if engine_factory_black else RandomAI()
    elif mode_key == "pvai":
        engine_factory = engine_lookup.get(chosen_engine) if chosen_engine else None
        ai_engine = engine_factory() if engine_factory else None
        ai_white = ai_engine if player_color == "B" else None
        ai_black = ai_engine if player_color == "W" else None
    else:
        ai_white = None
        ai_black = None

    controller = GameController(
        game=game_instance,
        ai_white=ai_white,
        ai_black=ai_black,
    )
    controller.set_ai_context(
        game_mode=mode_key,
        player_color=player_color,
        ai_white=ai_meta_from_engine(ai_white),
        ai_black=ai_meta_from_engine(ai_black),
    )
    return controller


def build_ai_from_meta(ai_meta):
    if not ai_meta:
        return None

    engine = ai_meta.get("engine")
    difficulty = ai_meta.get("difficulty", 0)

    if engine == "Random AI":
        return RandomAI()
    if engine == "Simple Heuristic AI":
        try:
            difficulty = int(difficulty)
        except (ValueError, TypeError):
            difficulty = 1
        difficulty = 1 if difficulty <= 1 else 2
        return SimpleHeuristicAI(difficulty=difficulty or 1)

    return RandomAI()
