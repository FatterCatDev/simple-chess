import faulthandler
import traceback

faulthandler.enable(all_threads=True)

from game.game import Game
from ai.simple_heuristic_ai import SimpleHeuristicAI


def run(max_games=200, max_plies=500):
    for game_index in range(1, max_games + 1):
        game = Game()
        ai_white = SimpleHeuristicAI(difficulty=2)
        ai_black = SimpleHeuristicAI(difficulty=2)

        try:
            for ply in range(1, max_plies + 1):
                ai = ai_white if game.current_turn == "white" else ai_black
                move = ai.get_move(game)
                if move is None:
                    break
                game.make_move(*move)
                if game.game_over:
                    break
            if game_index % 10 == 0:
                print(
                    f"progress game={game_index} ply={ply} "
                    f"game_over={game.game_over} draw={game.draw_reason}",
                    flush=True,
                )
        except Exception as exc:
            print(f"FAILED_GAME {game_index} PLY {ply}", flush=True)
            print(type(exc).__name__, str(exc), flush=True)
            print(traceback.format_exc(), flush=True)
            raise

    print(f"completed {max_games} games", flush=True)


if __name__ == "__main__":
    run()
