from ai.ai import RandomAI
from ai.simple_heuristic_ai import SimpleHeuristicAI
from gui.controller import GameController
from ai.uci_engine import UCIEngine
from pathlib import Path
import os
import sys

ENGINE_OPTIONS = [
    ("Random AI", lambda: RandomAI()),
    ("Simple Heuristic AI (Easy)", lambda: SimpleHeuristicAI(difficulty=1)),
    ("Simple Heuristic AI (Hard)", lambda: SimpleHeuristicAI(difficulty=2)),
    ("Stockfish (UCI)", lambda: stockfish_factory(difficulty=1)) # Placeholder path; replace with actual path to Stockfish binary
]

def find_app_base_path():
    """Determine the base path of the application, whether running as a script or a frozen executable."""
    if getattr(sys, 'frozen', False):
        # If the application is frozen (e.g., by PyInstaller), use the directory of the executable
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    else:
        # If running as a script, use the directory of this file
        return Path(__file__).parent.parent  # Adjust as needed based on your project structure

def resolve_stockfish_binary_path():
    base = find_app_base_path()
    candidates = [
        base / "ai/stockfish/windows/avx2/stockfish-windows-x86-64-avx2.exe",
        base / "ai/stockfish/windows/non-avx2/stockfish-windows-x86-64.exe",
        base / "src/ai/stockfish/windows/avx2/stockfish-windows-x86-64-avx2.exe",
        base / "src/ai/stockfish/windows/non-avx2/stockfish-windows-x86-64.exe",
    ]
    possible_paths = []
    primary_path = []
    secondary_path = []
    for path in candidates:
        if path.exists():
            possible_paths.append(path)
    for path in possible_paths:
        if "avx2" in str(path):
            primary_path.append(path)
        else:
            secondary_path.append(path)
    if not primary_path and not secondary_path:
        return None, None
    return primary_path[0], secondary_path[0] if secondary_path else None

def stockfish_factory(difficulty=1):
    binary_path, secondary_path = resolve_stockfish_binary_path()
    if binary_path is None:
        return RandomAI()  # Fallback to RandomAI if Stockfish binary is not found
    return UCIEngine(engine_name="Stockfish", binary_path=str(binary_path), difficulty=difficulty, secondary_binary_path=str(secondary_path) if secondary_path else None)

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
    if engine == "Stockfish":
        return stockfish_factory(difficulty=difficulty or 1)

    return RandomAI()
