import os
import tkinter as tk
from tkinter import ttk
from gui.controller import GameController
from game.game import Game
from PIL import Image, ImageTk


#--------------------------------Build the main application window--------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current file, will be used to locate resources like images

main = tk.Tk()
main.title("Simple Chess")
main.label = tk.Label(main, text="New Game", font=("Helvetica", 16))
main.label.pack(pady=10)
main.config(bg="#070015")
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

style.configure("WhiteSquare.TButton", background="#E7E7E7", relief="flat") # Set the background color for white squares to a light gray and remove the border relief
style.configure("BlackSquare.TButton", background="#555555", relief="flat") # Set the background color for black squares to a dark gray and remove the border relief
style.map("WhiteSquare.TButton", background=[("active", "#a8a8a8")], foreground=[("active", "#000")]) # Set the background color for white squares when active to a medium gray and the text color to black
style.map("BlackSquare.TButton", background=[("active", "#a8a8a8")], foreground=[("active", "#000")]) # Set the background color for black squares when active to a medium gray and the text color to black

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

def refresh_board():
    state = game_controller.get_state()
    for square, button in square_buttons.items():
        code = state["board"].get(square)  # e.g. "wP", "bK", or None
        if code:
            button.config(image=get_piece_image(code), text="")
        else:
            button.config(image="", text="")

def handle_click(square):
    game_controller.on_square_click(square)
    refresh_board()
    game_state = game_controller.get_state()
    main.label.config(text=f"Turn: {game_state['current_turn']} | Selected: {game_state['selected_square']}")

#--------------------------------Build the chess board UI--------------------------------

container = tk.Frame(main, bg="#070015")
container.pack(fill="both", expand=True)

square_buttons = {}  # Dictionary to hold references to the square buttons
game = Game()  # Initialize the game
game_controller = GameController(game)  # Initialize the game controller with the game

# Fixed square board size
tile = 64
piece_size = 60
board_size = tile * 8

board_frame = tk.Frame(container, width=board_size, height=board_size, bg="#070015")
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

refresh_board()  # Initial board setup

main.mainloop()