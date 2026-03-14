from cProfile import label
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ctypes
from ctypes import wintypes
import sys
from datetime import datetime
IS_WINDOWS = sys.platform.startswith("win")
if IS_WINDOWS:
    import winreg
from gui.controller import GameController
from game.game import Game
from PIL import Image, ImageTk
from utils.constants import GLOBAL_BUTTON_STYLE
from ai.ai import RandomAI
from ai.simple_heuristic_ai import SimpleHeuristicAI



def _windows_prefers_dark_app_mode() -> bool:
    """Return True when Windows personalization says apps should use dark mode."""
    if not IS_WINDOWS:
        return False

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(apps_use_light_theme) == 0
    except Exception:
        return True


def _apply_dark_title_bar(window: tk.Tk) -> None:
    if not IS_WINDOWS:
        return

    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetParent.restype = wintypes.HWND

        dwm_set_window_attribute = dwmapi.DwmSetWindowAttribute
        dwm_set_window_attribute.argtypes = [
            wintypes.HWND,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        dwm_set_window_attribute.restype = ctypes.c_long

        raw_hwnd = wintypes.HWND(window.winfo_id())
        hwnd = user32.GetParent(raw_hwnd) or raw_hwnd

        value = ctypes.c_int(1 if _windows_prefers_dark_app_mode() else 0)

        for attr in (20, 19):
            dwm_set_window_attribute(
                hwnd,
                wintypes.DWORD(attr),
                ctypes.byref(value),
                wintypes.DWORD(ctypes.sizeof(value)),
            )
    except Exception:
        pass
def run_app():

    #--------------------------------Build the main application window--------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current file, will be used to locate resources like images

    current_mode = "pvp"  # Default mode is player vs player

    main = tk.Tk()
    main.title("Simple Chess")
    main.config(bg=GLOBAL_BUTTON_STYLE["primary"])
    main.geometry("1000x800")
    main.update_idletasks()
    _apply_dark_title_bar(main)
    main.config(bg=GLOBAL_BUTTON_STYLE["primary"])

    geometryX = 0
    geometryY = 0

    main.geometry("+%d+%d"%(geometryX, geometryY))

    style = ttk.Style(main)
    style.theme_use("clam")

    top_bar = tk.Frame(main, bg="#1f2933", height=30)
    top_bar.pack(fill="x")
    top_bar.pack_propagate(False)

    main.label = tk.Label(main, text="New Game", font=("Helvetica", 16), bg=GLOBAL_BUTTON_STYLE["primary"], fg="#FFF")
    main.label.pack(pady=10)

    game_button = tk.Menubutton(
        top_bar,
        text="Game",
        bg="#1f2933",
        fg="#ffffff",
        activebackground=GLOBAL_BUTTON_STYLE["hovered"],
        activeforeground="#000000",
        relief="flat",
        borderwidth=0,
        padx=10,
        pady=4,
    )
    game_button.pack(side="left", padx=(6, 2), pady=2)

    game_menu = tk.Menu(
        game_button,
        tearoff=0,
        bg="#1f2933",
        fg="#ffffff",
        activebackground=GLOBAL_BUTTON_STYLE["hovered"],
        activeforeground="#000000",
    )
    game_menu.add_command(label="Save", command=lambda: handle_save())
    game_menu.add_command(label="Load", command=lambda: handle_load())
    game_menu.add_command(label="New", command=lambda: handle_new())
    game_button.config(menu=game_menu)

    style.configure(
        "WhiteSquare.TButton", 
        background=GLOBAL_BUTTON_STYLE["secondary"], 
        relief="flat"
        ) # Set the background color for white squares to a light gray and remove the border relief
    style.configure(
        "BlackSquare.TButton", 
        background=GLOBAL_BUTTON_STYLE["tertiary"], 
        relief="flat"
        ) # Set the background color for black squares to a dark gray and remove the border relief
    style.map(
        "WhiteSquare.TButton", 
        background=[("active", GLOBAL_BUTTON_STYLE["hovered"])], 
        foreground=[("active", "#000")]
        ) # Set the background color for white squares when active to a medium gray and the text color to black
    style.map(
        "BlackSquare.TButton", 
        background=[("active", GLOBAL_BUTTON_STYLE["hovered"])], 
        foreground=[("active", "#000")]
        ) # Set the background color for black squares when active to a medium gray and the text color to black

    style.configure(
        "History.Vertical.TScrollbar",
        background=GLOBAL_BUTTON_STYLE["tertiary"],
        troughcolor=GLOBAL_BUTTON_STYLE["sidebar_bg"],
        arrowcolor="#ffffff",
        bordercolor=GLOBAL_BUTTON_STYLE["sidebar_bg"],
        darkcolor=GLOBAL_BUTTON_STYLE["tertiary"],
        lightcolor=GLOBAL_BUTTON_STYLE["tertiary"],
        relief="flat",
    )
    style.map(
        "History.Vertical.TScrollbar",
        background=[("active", GLOBAL_BUTTON_STYLE["hovered"])],
        arrowcolor=[("active", "#000000")],
    )

    #--------------------------------Helpers-------------------------------------------------

    piece_images = {}

    ENGINE_OPTIONS = [
        ("Random AI", lambda: RandomAI()),
        ("Simple Heuristic AI (Easy)", lambda: SimpleHeuristicAI(difficulty=1)),
        ("Simple Heuristic AI (Hard)", lambda: SimpleHeuristicAI(difficulty=2))
        ]

    def mode_select(mode_key="pvp", engine_factory=None):
        if mode_key == "pvp":
            ai_white = None
            ai_black = None
        elif mode_key == "pvai":
            ai_white = None
            ai_black = engine_factory() if engine_factory else RandomAI()
        else:  # "aivai"
            ai_white = engine_factory() if engine_factory else RandomAI()
            ai_black = engine_factory() if engine_factory else RandomAI()
        return GameController(game, ai_white=ai_white, ai_black=ai_black)

    def get_piece_image(code: str):
        if code not in piece_images:
            path = os.path.join(BASE_DIR, "assets", f"{code}.png")
            image = Image.open(path)
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image = image.resize((piece_size, piece_size), Image.Resampling.LANCZOS)
            piece_images[code] = ImageTk.PhotoImage(image)
        return piece_images[code]

    def blend(hex1, hex2, t):
        # t: 0.0 -> hex1, 1.0 -> hex2
        h1 = hex1.lstrip("#")
        h2 = hex2.lstrip("#")
        r1, g1, b1 = int(h1[0:2], 16), int(h1[2:4], 16), int(h1[4:6], 16)
        r2, g2, b2 = int(h2[0:2], 16), int(h2[2:4], 16), int(h2[4:6], 16)
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    style.configure(
        "SelectedLight.TButton", 
        background=blend(GLOBAL_BUTTON_STYLE["selected"], GLOBAL_BUTTON_STYLE["secondary"], 0.5), 
        relief="flat"
        ) # Set the background color for selected squares to a medium gray and remove the border relief
    style.configure(
        "SelectedDark.TButton", 
        background=blend(GLOBAL_BUTTON_STYLE["selected"], GLOBAL_BUTTON_STYLE["tertiary"], 0.5), 
        relief="flat"
        ) # Set the background color for selected squares to a medium gray and remove the border relief
    style.configure(
        "LegalMoveLight.TButton", 
        background=blend(GLOBAL_BUTTON_STYLE["legal_move"], GLOBAL_BUTTON_STYLE["secondary"], 0.7), 
        relief="flat"
        ) # Set the background color for legal move squares to light green and remove the border relief
    style.configure(
        "LegalMoveDark.TButton", 
        background=blend(GLOBAL_BUTTON_STYLE["legal_move"], GLOBAL_BUTTON_STYLE["tertiary"], 0.7), 
        relief="flat"
        ) # Set the background color for legal move squares to light green and remove the border relief
    
    game_over_dialog_shown = False  # Flag to track if the game over dialog has been shown

    def ask_promotion_choice(color):
        """Show a modal dialog asking the player which piece to promote to."""
        result = {"choice": None}

        dialog = tk.Toplevel(main)
        dialog.title("Promote Pawn")
        dialog.config(bg=GLOBAL_BUTTON_STYLE["primary"])
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", lambda: [result.update({"choice": None}), dialog.destroy()])

        tk.Label(
            dialog, text="Choose promotion piece:",
            bg=GLOBAL_BUTTON_STYLE["primary"], fg="#FFF",
            font=("Helvetica", 12)
        ).pack(pady=(12, 6))

        btn_frame = tk.Frame(dialog, bg=GLOBAL_BUTTON_STYLE["primary"])
        btn_frame.pack(pady=(0, 12), padx=20)

        color_prefix = "w" if color == "W" else "b"
        choices = [("Queen", "Q"), ("Rook", "R"), ("Bishop", "B"), ("Knight", "N")]

        for label, piece_type in choices:
            code = color_prefix + piece_type
            try:
                img = get_piece_image(code)
                btn = ttk.Button(
                    btn_frame, image=img, style="Replay.TButton",
                    command=lambda pt=piece_type: [result.update({"choice": pt}), dialog.destroy()]
                )
                btn.image = img
            except Exception:
                btn = ttk.Button(
                    btn_frame, text=label, style="Replay.TButton",
                    command=lambda pt=piece_type: [result.update({"choice": pt}), dialog.destroy()]
                )
            btn.pack(side="left", padx=5)

        main.wait_window(dialog)
        return result["choice"]

    def _build_game_over_message(state):
        if not state["is_draw"]:
            return "Checkmate! White wins!" if state["current_turn"] == "W" else "Checkmate! Black wins!"

        draw_reason = state.get("draw_reason")
        match draw_reason:
            case "Stalemate":
                return "Stalemate! The game is a draw."
            case "Insufficient material":
                return "Draw due to insufficient material."
            case "Threefold repetition":
                return "Draw due to threefold repetition."
            case "Fifty-move rule":
                return "Draw due to fifty-move rule."
            case _:
                return "Draw!"
    
    def show_game_over_dialog(message):
        nonlocal game_over_dialog_shown
        if game_over_dialog_shown:
            return  # Dialog has already been shown, do not show again
        else:
            game_over_dialog_shown = True  # Set the flag to True to indicate the dialog has been shown
        
        game_over_dialog = tk.Toplevel(main)
        game_over_dialog.title("Game Over")
        game_over_dialog.config(bg=GLOBAL_BUTTON_STYLE["primary"])
        game_over_dialog.resizable(False, False)
        game_over_dialog.grab_set()
        game_over_dialog.protocol("WM_DELETE_WINDOW", game_over_dialog.destroy)
        # Create a label to display the game over message
        tk.Label(
            game_over_dialog, 
            text=message, 
            font=("Helvetica", 16, "bold"), 
            bg=GLOBAL_BUTTON_STYLE["primary"], 
            fg="#FFF"
        ).pack(pady=(12, 6))
        
        # Button frame
        btn_frame = tk.Frame(game_over_dialog, bg=GLOBAL_BUTTON_STYLE["primary"])
        ttk.Button(
            btn_frame,
            text="New Game",
            style="Replay.TButton",
            command=lambda: [game_over_dialog.destroy(), handle_new()]
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Save Game",
            style="Replay.TButton",
            command=handle_save
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Replay",
            style="Replay.TButton",
            command=lambda: [game_over_dialog.destroy(), handle_replay_start()]
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Close",
            style="Replay.TButton",
            command=game_over_dialog.destroy
        ).pack(side="left", padx=5)
        btn_frame.pack(pady=(0, 12), padx=20)

        game_over_dialog.update_idletasks()
        x = main.winfo_x() + (main.winfo_width() - game_over_dialog.winfo_width()) // 2
        y = main.winfo_y() + (main.winfo_height() - game_over_dialog.winfo_height()) // 2
        game_over_dialog.geometry(f"+{x}+{y}")

    def refresh_board():
        state = game_controller.get_state()
        move_list = state["move_list"]  # Use the history_list from the controller state
        selected_square = state["selected_square"]
        legal_moves = state["legal_moves"]
        replay = state["replay"]
        mid_replay = replay["active"]

        for square, button in square_buttons.items():
            code = state["board"].get(square)  # e.g. "wP", "bK", or None
            if code:
                button.config(image=get_piece_image(code), text="")
            else:
                button.config(image="", text="")
            if square == selected_square:
                if (int(square[1]) + ord(square[0]) - ord('a')) % 2 == 0:
                    button.config(style="SelectedLight.TButton")
                else:
                    button.config(style="SelectedDark.TButton")
            elif square in legal_moves:
                if (int(square[1]) + ord(square[0]) - ord('a')) % 2 == 0:
                    button.config(style="LegalMoveLight.TButton")
                else:
                    button.config(style="LegalMoveDark.TButton")
            else:
                sq_style = "WhiteSquare.TButton" if (int(square[1]) + ord(square[0]) - ord('a')) % 2 == 0 else "BlackSquare.TButton"
                button.config(style=sq_style)

        history_listbox.delete(0, "end")

        if not move_list:
            history_listbox.insert("end", "No moves yet.")
        else:
            for i in range(0, len(move_list), 2):
                move_number = (i // 2) + 1
                white_move = move_list[i]
                black_move = move_list[i+1] if i + 1 < len(move_list) else ""
                if black_move:
                    line = f"{move_number}. {white_move}, {black_move}"
                else:
                    line = f"{move_number}. {white_move}"
                history_listbox.insert("end", line)
        
        # Replay highlight (after listbox is populated)
        history_listbox.selection_clear(0, "end")
        replay_state = state["replay"]
        if replay_state["active"] and replay_state["index"] > 0 and move_list:
            row_index = (replay_state["index"] - 1) // 2
            if 0 <= row_index < history_listbox.size():
                history_listbox.selection_set(row_index)
                history_listbox.see(row_index)

        update_history_scrollbar_visibility()
        if state["game_over"] and not mid_replay:
            message = _build_game_over_message(state)
            show_game_over_dialog(message)


    def update_history_scrollbar_visibility():
        nonlocal history_scrollbar_visible

        history_listbox.update_idletasks()
        total_items = history_listbox.size()

        visible_rows = 0
        if total_items > 0:
            first_bbox = history_listbox.bbox(0)
            if first_bbox:
                row_height = first_bbox[3]
                if row_height > 0:
                    visible_rows = max(1, history_listbox.winfo_height() // row_height)

        if visible_rows <= 0:
            try:
                visible_rows = max(1, int(history_listbox.cget("height")))
            except Exception:
                visible_rows = 10

        needs_scroll = total_items > visible_rows

        if needs_scroll and not history_scrollbar_visible:
            history_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
            history_scrollbar_visible = True
        elif not needs_scroll and history_scrollbar_visible:
            history_scrollbar.pack_forget()
            history_scrollbar_visible = False

    def handle_click(square):
        selected = game_controller.selected_square
        is_promotion_attempt = False
        promotion_choice = None
        player_moved = False

        if selected:
            piece = game.board.get_piece_at(selected)
            if piece and piece.type == "P":
                rank = square[1]
                if (piece.color == "W" and rank == "8") or (piece.color == "B" and rank == "1"):
                    target_piece = game.board.get_piece_at(square)
                    is_reselect = (
                        target_piece and
                        target_piece.color == game.current_turn and
                        square != selected
                    )
                    if not is_reselect:
                        is_promotion_attempt = True
                        promotion_choice = ask_promotion_choice(piece.color)

        if is_promotion_attempt:
            if promotion_choice is not None:
                game_controller.last_error = None
                player_moved = game_controller.try_move(square, promotion_choice)
            else:
                game_controller.selected_square = None  # Player cancelled dialog
                player_moved = False
        else:
            player_moved = game_controller.on_square_click(square)

        if player_moved:
            if game_controller.should_ai_move():
                game_controller.make_ai_move()
                player_moved = False # Reset player_moved after AI move

        refresh_board()
        update_status_label()

    def update_status_label():
        move_list = game_controller.get_state()["move_list"]
        if not move_list:
            main.label.config(text="New Game")
            return
        color_name = {"W": "White", "B": "Black"}
        game_state = game_controller.get_state()
        selected_square = game_state["selected_square"] if game_state["selected_square"] else "-"
        replay_state = game_state["replay"]
        parts = [
            f"Turn: {color_name[game_state['current_turn']]}",
            f"Selected: {selected_square}",
        ]

        if replay_state["total"] > 0:
            parts.append(f"Replay: {replay_state['index']}/{replay_state['total']}")

        if game_state["is_draw"]:
            parts.append(f"Draw: {game_state['draw_reason'] or 'draw'}")
        elif game_state["game_over"]:
            parts.append(f"Checkmate: {color_name[game_state['current_turn']]} wins")
        elif game_state["is_in_check"]:
            parts.append(f"Check")

        if game_state["last_error"]:
            parts.append(f"Error: {game_state['last_error']}")

        main.label.config(text=" | ".join(parts))

    def overlay_cancel_timers():
        nonlocal overlay_fade_after_id, overlay_hide_after_id
        if overlay_fade_after_id is not None:
            main.after_cancel(overlay_fade_after_id)
            overlay_fade_after_id = None
        if overlay_hide_after_id is not None:
            main.after_cancel(overlay_hide_after_id)
            overlay_hide_after_id = None

    def fade_step(step, total_steps):
        nonlocal overlay_fade_after_id, overlay_hide_after_id

        progress = step / total_steps
        current_bg = blend(overlay_start_bg, overlay_end_bg, progress)
        current_fg = blend(overlay_start_fg, overlay_end_fg, progress)

        board_success_label.config(bg=current_bg, fg=current_fg)

        if step < total_steps:
            overlay_fade_after_id = main.after(50, lambda: fade_step(step + 1, total_steps))
            return

        board_success_label.place_forget()
        board_success_label.config(text="", bg=overlay_start_bg, fg=overlay_start_fg)
        overlay_fade_after_id = None
        overlay_hide_after_id = None

    def show_board_success(message):
        nonlocal overlay_hide_after_id

        overlay_cancel_timers()
        board_success_label.config(text=message, bg=overlay_start_bg, fg=overlay_start_fg)
        board_success_label.place(relx=0.5, rely=0.5, anchor="center")
        board_success_label.lift()
        overlay_hide_after_id = main.after(250, lambda: fade_step(0, 20))

    def player_labels(ai_white=None, ai_black=None): # Temporary AI naming, will be replaced with actual AI instances later
        player_bottom = "Player 1"
        player_top = "Player 2"
        if ai_white and ai_black:
            player_bottom = ai_white.name
            player_top = ai_black.name
        elif ai_white:
            player_bottom = ai_white.name
            player_top = "Player 2"
        elif ai_black:
            player_bottom = "Player 1"
            player_top = ai_black.name
        return player_top, player_bottom

    def refresh_player_labels():
        top_label, bottom_label = player_labels(ai_white=game_controller.ai_white, ai_black=game_controller.ai_black)
        player_one_label.config(text=top_label)
        player_two_label.config(text=bottom_label)

    def show_mode_dialog():
        nonlocal current_mode, game_controller
        mode_dialog = tk.Toplevel(main)
        mode_dialog.title("Select Game Mode")
        mode_dialog.config(bg=GLOBAL_BUTTON_STYLE["primary"])
        mode_dialog.resizable(False, False)
        mode_dialog.grab_set()
        mode_dialog.protocol("WM_DELETE_WINDOW", mode_dialog.destroy)

        selected_engine = tk.StringVar(value=ENGINE_OPTIONS[0][0])  # Default to the first engine option
        engine_frame = tk.Frame(mode_dialog, bg=GLOBAL_BUTTON_STYLE["primary"])
        tk.Label(
            engine_frame,
            text="Select AI Engine:",
            font=("Helvetica", 12),
            bg=GLOBAL_BUTTON_STYLE["primary"],
            fg="#FFF"
        ).pack(pady=(12, 6))
        engine_options = tk.OptionMenu(
            engine_frame,
            selected_engine,
            *[label for label, _ in ENGINE_OPTIONS]
        )
        engine_options.pack(pady=(0, 12), padx=20)
        engine_options.config(bg=GLOBAL_BUTTON_STYLE["primary"], fg="#FFF", highlightthickness=0, relief="flat")

        tk.Label(
            mode_dialog,
            text="Select Game Mode:",
            font=("Helvetica", 12),
            bg=GLOBAL_BUTTON_STYLE["primary"],
            fg="#FFF"
        ).pack(pady=(12, 6))

        btn_frame = tk.Frame(mode_dialog, bg=GLOBAL_BUTTON_STYLE["primary"])
        btn_frame.pack(pady=(0, 12), padx=20)
        engine_frame.pack(pady=(0, 12), padx=20)

        modes = [("Player vs Player", "pvp"), ("Player vs AI", "pvai"), ("AI vs AI", "aivai")]

        selected_mode = tk.StringVar(value=current_mode)

        def update_engine_visibility(*_):
            if selected_mode.get() == "pvp":
                engine_frame.pack_forget()
            else:
                engine_frame.pack(pady=(0, 12), padx=20)

        selected_mode.trace_add("write", update_engine_visibility)
        update_engine_visibility()  # Initial call to set visibility based on default mode
        
        for label, mode_key in modes:
            tk.Radiobutton(
                btn_frame,
                text=label,
                variable=selected_mode,
                value=mode_key,
                bg=GLOBAL_BUTTON_STYLE["primary"],
                fg="#FFF",
                selectcolor="#000000",
                activebackground=GLOBAL_BUTTON_STYLE["hovered"],
                activeforeground="#000"
            ).pack(anchor="w", pady=2)

        action = {"confirmed": False}

        def on_start():
            action["confirmed"] = True
            mode_dialog.destroy()

        def on_cancel():
            mode_dialog.destroy()

        action_frame = tk.Frame(mode_dialog, bg=GLOBAL_BUTTON_STYLE["primary"])
        action_frame.pack(pady=(0, 12), padx=20)
        ttk.Button(action_frame, text="Start", style="Replay.TButton", command=on_start).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Cancel", style="Replay.TButton", command=on_cancel).pack(side="left", padx=5)

        main.wait_window(mode_dialog)
        return (selected_mode.get(), selected_engine.get()) if action["confirmed"] else None


    #--------------------------------Build the chess board and history UI--------------------------------

    container = tk.Frame(main, bg=GLOBAL_BUTTON_STYLE["primary"])
    container.pack(fill="both", expand=True)
    main_content = tk.Frame(container, bg=GLOBAL_BUTTON_STYLE["primary"])
    main_content.pack(fill="both", expand=True)
    main_content.grid_rowconfigure(0, weight=1)
    main_content.grid_columnconfigure(0, weight=1)
    main_content.grid_columnconfigure(1, weight=0)  # History column does not expand

    left_frame = tk.Frame(main_content, bg=GLOBAL_BUTTON_STYLE["primary"])
    left_frame.grid(row=0, column=0, sticky="nsew")
    content_frame = tk.Frame(left_frame, bg=GLOBAL_BUTTON_STYLE["primary"])
    content_frame.pack(fill="both", side="top", expand=True)
    middle_board_holder = tk.Frame(content_frame, bg=GLOBAL_BUTTON_STYLE["primary"], width=64*8, height=64*8)

    right_frame = tk.Frame(main_content, bg=GLOBAL_BUTTON_STYLE["sidebar_bg"], width=220)
    right_frame.grid(row=0, column=1, sticky="ns")
    right_frame.grid_propagate(False)  # keep exact width/height

    tk.Label(right_frame, text="Move History", font=("Helvetica", 14), bg=GLOBAL_BUTTON_STYLE["sidebar_bg"], fg="#FFF").pack(pady=10)
    history_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", style="History.Vertical.TScrollbar")
    history_listbox = tk.Listbox(
        right_frame, 
        yscrollcommand=history_scrollbar.set, 
        bg=GLOBAL_BUTTON_STYLE["sidebar_bg"], fg="#FFF", 
        selectbackground=GLOBAL_BUTTON_STYLE["hovered"], 
        highlightthickness=0, bd=0
        )
    history_scrollbar.config(command=history_listbox.yview)
    history_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)
    history_scrollbar_visible = True
    history_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    history_listbox.insert("end", "No moves yet.")

    square_buttons = {}  # Dictionary to hold references to the square buttons
    game = Game()  # Initialize the game
    ai_black = RandomAI()  # temporary AI for black
    game_controller = mode_select(current_mode)  # Hardcoded for pvp for now.


    # Fixed square board size
    tile = 64
    piece_size = 60
    board_size = tile * 8
    overlay_start_bg = "#1f2933"
    overlay_start_fg = "#d9f99d"
    overlay_end_bg = GLOBAL_BUTTON_STYLE["primary"]
    overlay_end_fg = overlay_end_bg
    overlay_fade_after_id = None
    overlay_hide_after_id = None

    top_label_name, bottom_label_name = player_labels(ai_white=game_controller.ai_white, ai_black=game_controller.ai_black)  # Temporary AI naming, will be replaced with actual AI instances later

    top_label_frame = tk.Frame(content_frame, bg=GLOBAL_BUTTON_STYLE["primary"], height=30)
    bottom_label_frame = tk.Frame(content_frame, bg=GLOBAL_BUTTON_STYLE["primary"], height=30)

    player_one_label = tk.Label(
        top_label_frame,
        text=top_label_name,
        font=("Helvetica", 12),
        bg=GLOBAL_BUTTON_STYLE["primary"],
        fg="#FFF"
    )
    player_one_label.pack(side="top", fill="x", pady=5)
    
    player_two_label = tk.Label(
        bottom_label_frame,
        text=bottom_label_name,
        font=("Helvetica", 12),
        bg=GLOBAL_BUTTON_STYLE["primary"],
        fg="#FFF"
    )
    player_two_label.pack(side="top", fill="x", pady=5)

    board_frame = tk.Frame(content_frame, width=board_size, height=board_size, bg=GLOBAL_BUTTON_STYLE["primary"])
    board_frame.grid_propagate(False)  # keep exact width/height

    board_success_label = tk.Label(
        board_frame,
        text="",
        font=("Helvetica", 16, "bold"),
        bg=overlay_start_bg,
        fg=overlay_start_fg,
        padx=18,
        pady=10,
        bd=1,
        relief="solid"
    )
    board_success_label.place_forget()

    for r in range(8):
        board_frame.grid_rowconfigure(r, minsize=tile, weight=1, uniform="row")
    for c in range(8):
        board_frame.grid_columnconfigure(c, minsize=tile, weight=1, uniform="col")

    for i in range(8):
        for j in range(8):
            file = "abcdefgh"[j]
            rank = str(8 - i)
            sq_style = "WhiteSquare.TButton" if (i + j) % 2 == 0 else "BlackSquare.TButton"
            b = ttk.Button(
                board_frame,
                text="",
                style=sq_style, 
                command=lambda sq=file+rank: handle_click(sq))
            b.grid(row=i, column=j, sticky="nsew")
            b.config(compound="center", padding=0, text="")  # Center the image on the button
            square_buttons[file+rank] = b  # Store the button reference in the dictionary

    #-------------------------------Replayer Controls--------------------------------
    controls_frame = tk.Frame(left_frame, bg=GLOBAL_BUTTON_STYLE["primary"])
    controls = tk.Frame(controls_frame, bg=GLOBAL_BUTTON_STYLE["primary"])
    controls.pack(side="top", pady=10)  # Place the controls at the bottom of the left frame
    replay_button_stype = ttk.Style()
    replay_button_stype.configure("Replay.TButton", background=GLOBAL_BUTTON_STYLE["secondary"], relief="flat", padding=5)
    replay_button_stype.map("Replay.TButton", background=[("active", GLOBAL_BUTTON_STYLE["hovered"])], foreground=[("active", "#000")])  # Set the background color for replay buttons when active to a medium gray and the text color to black

    top_label_frame.pack(side="top", fill="x", expand= True)
    middle_board_holder.pack(side="top", fill="both", expand=True)
    board_frame.place(in_=middle_board_holder, relx=0.5, rely=0.5, anchor="center")
    bottom_label_frame.pack(side="top", fill="x", expand=True)
    controls_frame.pack(side="bottom", fill="x")


    def handle_save():
        default_filename = f"Game_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.json"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Game State"
        )
        if file_path:
            try:
                ok = game_controller.save_notation_to_file(file_path)
                if ok:
                    game_controller.last_error = None
                    update_status_label()
                    show_board_success("Game saved")
                else:
                    error = game_controller.last_error or "Unknown error"
                    messagebox.showerror("Save Error", f"Failed to save game state: {error}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save game state: {e}")

    def handle_load():
        nonlocal game_over_dialog_shown
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Game State"
        )
        if file_path:
            try:
                ok = game_controller.load_notation_from_file(file_path)
                if ok:
                    game_over_dialog_shown = False  # Reset the flag when loading a game
                    game_controller.last_error = None
                    refresh_board()
                    update_status_label()
                    show_board_success("Game loaded")
                else:
                    error = game_controller.last_error or "Unknown error"
                    messagebox.showerror("Load Error", f"Failed to load game state: {error}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load game state: {e}")

    def handle_new():
        nonlocal game, game_controller, game_over_dialog_shown, current_mode
        chosen_option = show_mode_dialog()
        if chosen_option is None:
            return  # User cancelled the mode selection dialog
        chosen_mode, chosen_engine = chosen_option
        if not chosen_mode:
            return  # User cancelled the mode selection dialog
        current_mode = chosen_mode
        engine_lookup = dict(ENGINE_OPTIONS)
        engine_factory = engine_lookup.get(chosen_engine) if chosen_engine else None
        game_over_dialog_shown = False  # Reset the flag when starting a new game
        game = Game()
        game_controller = mode_select(current_mode, engine_factory)  # Hardcoded for pvp for now.
        refresh_board()
        refresh_player_labels()
        update_status_label()
        show_board_success("New game started")


    def handle_undo():
        game_controller.undo()
        refresh_board()
        update_status_label()

    def handle_reset():
        game_controller.reset()
        refresh_board()
        refresh_player_labels()
        update_status_label()

    def handle_replay_start():
        game_controller.replay_start()
        refresh_board()
        refresh_player_labels()
        update_status_label()

    def handle_replay_previous():
        game_controller.replay_previous()
        refresh_board()
        refresh_player_labels()
        update_status_label()

    def handle_replay_next():
        game_controller.replay_next()
        refresh_board()
        refresh_player_labels()
        update_status_label()

    def handle_replay_end():
        game_controller.replay_end()
        refresh_board()
        refresh_player_labels()
        update_status_label()

    undo_button = ttk.Button(controls, text="Undo", command=handle_undo, style="Replay.TButton")
    undo_button.pack(side="left", padx=5)
    reset_button = ttk.Button(controls, text="Reset", command=handle_reset, style="Replay.TButton")
    reset_button.pack(side="left", padx=5)
    replay_start_button = ttk.Button(controls, text="|<", command=handle_replay_start, style="Replay.TButton")
    replay_start_button.pack(side="left", padx=5)
    replay_previous_button = ttk.Button(controls, text="<", command=handle_replay_previous, style="Replay.TButton")
    replay_previous_button.pack(side="left", padx=5)
    replay_next_button = ttk.Button(controls, text=">", command=handle_replay_next, style="Replay.TButton")
    replay_next_button.pack(side="left", padx=5)
    replay_end_button = ttk.Button(controls, text=">|", command=handle_replay_end, style="Replay.TButton")
    replay_end_button.pack(side="left", padx=5)


    result = show_mode_dialog()
    if result:
        chosen_mode, chosen_engine = result
        if chosen_mode:
            current_mode = chosen_mode
            engine_lookup = dict(ENGINE_OPTIONS)
            engine_factory = engine_lookup.get(chosen_engine) if chosen_engine else None
            game_controller = mode_select(current_mode, engine_factory)

    refresh_board()  # Initial board setup
    refresh_player_labels()  # Initial player labels setup

    main.mainloop()

if __name__ == "__main__":
    run_app()
