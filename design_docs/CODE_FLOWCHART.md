# Simple Chess Code Flowchart (Modules, Classes, Functions)

Last verified: 2026-03-16

This chart focuses on runtime execution paths (app startup, move handling, AI turns, simulation engine, save/load/replay).

## 1) Module + Class Overview

- src/main.py
  - main()
- src/gui/app.py
  - run_app()
  - UI handlers: handle_click(), auto_play_step(), handle_save(), handle_load(), handle_new()
- src/gui/ai_mode.py
  - build_controller_for_mode()
  - build_ai_from_meta()
  - ai_meta_from_engine()
- src/gui/controller.py
  - class GameController
    - on_square_click(), try_move(), make_ai_move(), should_ai_move()
    - replay_start(), replay_next(), replay_previous(), replay_end()
    - save_notation_to_file(), load_notation_from_file()
- src/game/game.py
  - class Game
    - make_move(), undo_move(), get_all_valid_moves(), get_legal_moves()
    - replay_start()/next()/previous()/end(), export_notation(), load_notation()
- src/game/standard_chess_rules.py
  - class StandardChessRules
    - is_valid_move() + piece-specific validators
- src/ai/ai.py
  - class AIEngine
  - class RandomAI
- src/ai/simple_heuristic_ai.py
  - class SimpleHeuristicAI
    - get_move(), _best_greedy_move(), _best_lookahead_move()
- src/ai/sim_state.py
  - PieceState, LastMoveState, AIState (immutable search state)
- src/ai/sim_adapter.py
  - game_to_ai_state(), apply_move_on_state(), generate_legal_moves_on_state(), is_in_check_state(), etc.

## 2) Runtime Flowchart (Bubbles + Variable-Labeled Edges)

```mermaid
flowchart TD

%% Entry
A((main.main)) -->|calls run_app()| B((gui.app.run_app))

%% Setup
B -->|mode_key, player_color, chosen_engine, chosen_white_engine, chosen_black_engine| C((gui.ai_mode.build_controller_for_mode))
C -->|game, ai_white, ai_black| D((GameController.__init__))
C -->|game_mode, player_color, ai_white_meta, ai_black_meta| E((GameController.set_ai_context))

%% Player move path
B -->|square| F((handle_click))
F -->|position| G((GameController.on_square_click))
G -->|to_position, promotion_choice| H((GameController.try_move))
H -->|from_position=selected_square, to_position, promotion_choice| I((Game.make_move))
I -->|state updates: board, move_history, last_move, is_in_check, game_over, draw flags| J((GameController._sync_history_list))
J -->|move_list| K((refresh_board / update_status_label))

%% AI loop path
K -->|if should_ai_move()| L((auto_play_step))
L -->|current_turn, ai_white, ai_black| M((GameController.should_ai_move))
L -->|game| N((GameController.make_ai_move))
N -->|game| O((AIEngine.get_move))

%% AI polymorphism
O --> P((RandomAI.get_move))
O --> Q((SimpleHeuristicAI.get_move))
P -->|all_moves = game.get_all_valid_moves(game.current_turn)| R((Game.get_all_valid_moves))

%% Heuristic easy
Q -->|difficulty==1| S((_best_greedy_move))
S -->|all_moves, from_square, to_square| R

%% Heuristic hard + simulation
Q -->|difficulty>=2, moves| T((_best_lookahead_move))
T -->|root_state = game_to_ai_state(game)| U((sim_adapter.game_to_ai_state))
T -->|state, from_square, to_square| V((sim_adapter.apply_move_on_state))
T -->|state| W((sim_adapter.generate_legal_moves_on_state))
T -->|state, color| X((sim_adapter.is_in_check_state))
T -->|cache keys from AIState| Y((_cached_legal_moves / _cached_in_check / _cached_opponent_best_reply_score))

%% state internals
U -->|pieces, current_turn, last_move, halfmove_clock, flags| Z((AIState))
V -->|from_square, to_square, promotion_choice| Z
W -->|piece_map, pseudo_targets, check filter| Z

%% AI move commit
N -->|from_sq, to_sq| AA((GameController.select_square))
AA -->|to_sq| H

%% Save / Load
B -->|path| AB((handle_save))
AB -->|path, ai_context, moves| AC((GameController.save_notation_to_file))
AC -->|notation = game.export_notation() OR replay_notation| AD((Game.export_notation))

B -->|path| AE((handle_load))
AE -->|path| AF((GameController.load_notation_from_file))
AF -->|moves| AG((GameController.load_notation))
AG -->|notation_list| AH((Game.load_notation))
AH -->|replay_start(notation), replayer(san)| AI((Game replay pipeline))

%% Replay controls
B -->|action=start/next/previous/end| AJ((replay button handlers))
AJ -->|replay_start/next/previous/end| AK((GameController replay methods))
AK -->|replay_start/next/previous/end| AI

%% Rules layer usage
I -->|from_position, to_position, last_move| AL((StandardChessRules.is_valid_move))
R -->|from_position, to_position, last_move| AL

```

## 3) Key Edge Variables (Quick Reference)

- Startup setup
  - run_app -> build_controller_for_mode
    - mode_key
    - player_color
    - chosen_engine / chosen_white_engine / chosen_black_engine
- Player move
  - handle_click -> on_square_click
    - position
  - try_move -> Game.make_move
    - from_position
    - to_position
    - promotion_choice
- AI turn
  - make_ai_move -> ai.get_move
    - game
  - SimpleHeuristic hard path
    - root_state = game_to_ai_state(game)
    - apply_move_on_state(state, from_square, to_square, promotion_choice)
    - generate_legal_moves_on_state(state)
    - is_in_check_state(state, color)
- Save/Load
  - save_notation_to_file
    - payload: format, version, moves, game_mode, player_color, ai_white, ai_black
  - load_notation_from_file
    - moves (SAN-lite list)

## 4) Notes

- Hard Simple Heuristic AI now avoids live undo-loop search and uses AIState simulation calls.
- Autoplay loop is non-overlapping (running guard), so AI ticks do not re-enter while executing.
- Legal move parity between state engine and live engine is validated in tests.
