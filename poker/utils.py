COLOR_CODES = {
    "red": "⫷",
    "blue": "⫸",
    "purple": "⟐",
    "yellow": "⟡",
    "gray": "⫿",
    "green": "⟑",
    "white": "␛" 
}

COLORS = {
    code: name
    for name, code in COLOR_CODES.items()
}

EXACT_COLORS = {
    "red": (255, 64, 64),
    "blue": (64, 140, 255),
    "purple": (124, 58, 255),
    "yellow": (255, 168, 54),
    "gray": (90, 90, 90),
    "green": (72, 204, 120),
    "white": (245, 245, 245),
    "magenta": (255, 0, 255),
    "cyan": (0, 210, 210),
}
