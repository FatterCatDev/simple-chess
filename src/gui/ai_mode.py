from ai.ai import RandomAI
from ai.simple_heuristic_ai import SimpleHeuristicAI
from gui.controller import GameController
from ai.uci_engine import UCIEngine
from pathlib import Path
import sys

ENGINE_OPTIONS = {
    "Random AI": {"min": 1, "max": 1, "default": 1, "factory": lambda difficulty=1: RandomAI()},
    "Simple Heuristic AI": {"min": 1, "max": 2, "default": 1, "factory": lambda difficulty=1: simple_heuristic_ai_factory(difficulty)},
    "Stockfish": {"min": 1, "max": 10, "default": 1, "factory": lambda difficulty=1: stockfish_factory(difficulty)},
}

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
    if sys.platform.startswith("win"): # Windows
        candidates = [
            base / "ai/stockfish/windows/avx2/stockfish-windows-x86-64-avx2.exe",
            base / "ai/stockfish/windows/non-avx2/stockfish-windows-x86-64.exe",
            base / "src/ai/stockfish/windows/avx2/stockfish-windows-x86-64-avx2.exe",
            base / "src/ai/stockfish/windows/non-avx2/stockfish-windows-x86-64.exe",
        ]
    elif sys.platform.startswith("darwin"):  # macOS
        candidates = [
            base / "ai/stockfish/macos/avx2/stockfish-macos-x86-64-avx2",
            base / "ai/stockfish/macos/non-avx2/stockfish-macos-x86-64",
            base / "src/ai/stockfish/macos/avx2/stockfish-macos-x86-64-avx2",
            base / "src/ai/stockfish/macos/non-avx2/stockfish-macos-x86-64",
        ]
    else:  # Assume Linux or other Unix-like OS
        candidates = [
            base / "ai/stockfish/ubuntu/avx2/stockfish-ubuntu-x86-64-avx2",
            base / "ai/stockfish/ubuntu/non-avx2/stockfish-ubuntu-x86-64",
            base / "src/ai/stockfish/ubuntu/avx2/stockfish-ubuntu-x86-64-avx2",
            base / "src/ai/stockfish/ubuntu/non-avx2/stockfish-ubuntu-x86-64",
        ]
    possible_paths = []
    primary_path = []
    secondary_path = []
    for path in candidates:
        if path.exists():
            possible_paths.append(path)
    for path in possible_paths:
        p = path.as_posix()
        if "/non-avx2/" in p:
            secondary_path.append(path)
        elif "/avx2/" in p:
            primary_path.append(path)
    if not primary_path and not secondary_path:
        return None, None
    elif primary_path and not secondary_path:
        return primary_path[0], None
    elif not primary_path and secondary_path:
        return secondary_path[0], None
    return primary_path[0], secondary_path[0] if secondary_path else None

def simple_heuristic_ai_factory(difficulty=1):
    return SimpleHeuristicAI(difficulty=difficulty)

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
    chosen_white_difficulty=None,
    chosen_black_difficulty=None,
    chosen_pvai_difficulty=None,
):

    if mode_key == "aivai":
        white_engine = ENGINE_OPTIONS.get(chosen_white_engine, ENGINE_OPTIONS["Random AI"]) if chosen_white_engine else ENGINE_OPTIONS["Random AI"]
        black_engine = ENGINE_OPTIONS.get(chosen_black_engine, ENGINE_OPTIONS["Random AI"]) if chosen_black_engine else ENGINE_OPTIONS["Random AI"]
        white_diff = chosen_white_difficulty if chosen_white_difficulty is not None else white_engine["default"]
        black_diff = chosen_black_difficulty if chosen_black_difficulty is not None else black_engine["default"]
        ai_white = white_engine["factory"](white_diff) if white_engine else RandomAI()
        ai_black = black_engine["factory"](black_diff) if black_engine else RandomAI()
    elif mode_key == "pvai":
        engine = ENGINE_OPTIONS.get(chosen_engine, ENGINE_OPTIONS["Random AI"]) if chosen_engine else ENGINE_OPTIONS["Random AI"]
        pvai_diff = chosen_pvai_difficulty if chosen_pvai_difficulty is not None else engine["default"]
        ai_engine = engine["factory"](pvai_diff) if engine else RandomAI()
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
