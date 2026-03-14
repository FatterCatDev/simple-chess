
PIECE_TYPES = {
    "pawn": "P",
    "knight": "N",
    "bishop": "B",
    "rook": "R",
    "queen": "Q",
    "king": "K"
}

COLOR = {
    "white": "W",
    "black": "B"
}

FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']

PIECE_SYMBOLS = {
    "W": {
        "P": "♙",
        "N": "♘",
        "B": "♗",
        "R": "♖",
        "Q": "♕",
        "K": "♔"
    },
    "B": {
        "P": "♟",
        "N": "♞",
        "B": "♝",
        "R": "♜",
        "Q": "♛",
        "K": "♚"
    }
}

GLOBAL_BUTTON_STYLE = {
    "primary": "#221D33",
    "secondary": "#D0C7EB",
    "tertiary": "#3B1F8D",
    "danger": "#FF4500",
    "hovered": "#75689B",
    "selected": "#5D84CA",
    "legal_move": "#90EE90",
    "sidebar_bg": "#2C2542",
}

PIECE_VALUES = {
    'P': 1,  # Pawn
    'N': 3,  # Knight
    'B': 3,  # Bishop
    'R': 5,  # Rook
    'Q': 9,  # Queen
    'K': 0   # King (not captured, so value is 0)
}