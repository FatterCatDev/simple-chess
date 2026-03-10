import os
import tkinter as tk
from tkinter import ttk
from gui.controller import GameController
from game.game import Game
from PIL import Image, ImageTk
from utils.constants import GLOBAL_BUTTON_STYLE


#--------------------------------Build the main application window--------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current file, will be used to locate resources like images

main = tk.Tk()
main.title("Simple Chess")
main.label = tk.Label(main, text="New Game", font=("Helvetica", 16))
main.label.pack(pady=10)
main.config(bg=GLOBAL_BUTTON_STYLE["primary"])
main.geometry("800x700")
main.update_idletasks()

geometryX = 0
geometryY = 0

main.geometry("+%d+%d"%(geometryX, geometryY))

style = ttk.Style(main)
style.theme_use("clam")

menu = tk.Menu(main)
main.config(menu=menu)
menu_0 = tk.Menu(menu, tearoff=0)
menu_0.add_command(label="New", command=lambda: print("New clicked"))
menu_0.add_command(label="Open", command=lambda: print("Open clicked"))
menu.add_cascade(label="File", menu=menu_0)
menu_1 = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Edit", menu=menu_1)

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

#--------------------------------Helpers-------------------------------------------------

piece_images = {}

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

def refresh_board():
    state = game_controller.get_state()
    selected_square = state["selected_square"]
    legal_moves = state["legal_moves"]
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

def handle_click(square):
    game_controller.on_square_click(square)
    refresh_board()
    update_status_label()

def update_status_label():
    game_state = game_controller.get_state()
    selected_square = game_state["selected_square"] if game_state["selected_square"] else "-"
    parts = [
        f"Turn: {game_state['current_turn']}",
        f"Selected: {selected_square}",
    ]

    if game_state["is_draw"]:
        parts.append(f"Draw: {game_state['draw_reason'] or 'draw'}")
    elif game_state["game_over"]:
        parts.append(f"Checkmate: {game_state['current_turn']} wins")
    elif game_state["is_in_check"]:
        parts.append(f"Check")

    if game_state["last_error"]:
        parts.append(f"Error: {game_state['last_error']}")

    main.label.config(text=" | ".join(parts))

#--------------------------------Build the chess board UI--------------------------------

container = tk.Frame(main, bg=GLOBAL_BUTTON_STYLE["primary"])
container.pack(fill="both", expand=True)

square_buttons = {}  # Dictionary to hold references to the square buttons
game = Game()  # Initialize the game
game_controller = GameController(game)  # Initialize the game controller with the game

# Fixed square board size
tile = 64
piece_size = 60
board_size = tile * 8

board_frame = tk.Frame(container, width=board_size, height=board_size, bg=GLOBAL_BUTTON_STYLE["primary"])
board_frame.place(relx=0.5, rely=0.5, anchor="center")
board_frame.grid_propagate(False)  # keep exact width/height

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

controls = tk.Frame(container, bg=GLOBAL_BUTTON_STYLE["primary"])
controls.pack(pady=7)
replay_button_stype = ttk.Style()
replay_button_stype.configure("Replay.TButton", background=GLOBAL_BUTTON_STYLE["secondary"], relief="flat", padding=5)
replay_button_stype.map("Replay.TButton", background=[("active", GLOBAL_BUTTON_STYLE["hovered"])], foreground=[("active", "#000")])  # Set the background color for replay buttons when active to a medium gray and the text color to black

def handle_undo():
    game_controller.undo()
    refresh_board()
    update_status_label()

def handle_reset():
    game_controller.reset()
    refresh_board()
    main.label.config(text="New Game")

undo_button = ttk.Button(controls, text="Undo", command=handle_undo, style="Replay.TButton")
undo_button.pack(side="left", padx=5)
reset_button = ttk.Button(controls, text="Reset", command=handle_reset, style="Replay.TButton")
reset_button.pack(side="left", padx=5)

refresh_board()  # Initial board setup

main.mainloop()