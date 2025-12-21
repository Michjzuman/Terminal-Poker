import math

import utils

class Card:
    def __init__(self, rank, suit, x, y):
        self.rank = rank
        self.suit = suit
        self.x = x
        self.y = y
   
    def draw(self, canvas):
        color = {
            "H": utils.COLOR_CODES["red"],
            "C": utils.COLOR_CODES["purple"],
            "D": utils.COLOR_CODES["yellow"],
            "S": utils.COLOR_CODES["blue"],
            "B": utils.COLOR_CODES["gray"]
        }[self.suit]
        s = {
            "H": "♥",
            "C": "♣",
            "D": "♦",
            "S": "♠",
            "B": ""
        }[self.suit]
        
        if self.rank == "K":
            design = [
                f"┌───────┐",
                f"│  www  │",
                f"│  [{s}]  │",
                f"│ _/_\_ │",
                f"││+ † +││",
                f"│ - - - │",
                f"└───────┘",
                f"   K {s}   "
            ]
        elif self.rank == "Q":
            design = [
                f"┌───────┐",
                f"│  www  │",
                f"│  ({s})  │",
                f"│ _)*(_ │",
                f"│(~~V~~)│",
                f"│ - - - │",
                f"└───────┘",
                f"   Q {s}   "
            ]
        elif self.rank == "J":
            design = [
                f"┌───────┐",
                f"│  ,=~  │",
                f"│  [{s}{'}'}  │",
                f"│ _/_\_ │",
                f"│|\ |:/|│",
                f"│ - - - │",
                f"└───────┘",
                f"   J {s}   "
            ]
        else:
            design = [
                f"┌───────┐",
                f"│ {s if not self.rank in ['A', '2', '3'] else ' '} {s if self.rank in ['2', '3'] else ' '} {s if not self.rank in ['A', '2', '3'] else ' '} │",
                f"│   {s if self.rank in ['7', '8', '9', '10'] else ' '}   │",
                f"│ {s if self.rank in ['6', '7', '8', '9', '10'] else ' '} {s if self.rank in ['A', '3', '5'] else ' '} {s if self.rank in ['6', '7', '8', '9', '10'] else ' '} │",
                f"│ {s if self.rank in ['9', '10'] else ' '} {s if self.rank in ['8', '10'] else ' '} {s if self.rank in ['9', '10'] else ' '} │",
                f"│ {s if not self.rank in ['A', '2', '3'] else ' '} {s if self.rank in ['2', '3'] else ' '} {s if not self.rank in ['A', '2', '3'] else ' '} │",
                f"└───────┘",
                f"  {'10' if self.rank == '10' else ' ' + self.rank[-1]} {s}   "
            ]
        
        result = design[:1]
        
        for line in design[1:-2]:
            result.append(f"{line[0]}{color}{line[1:-1]}{utils.COLOR_CODES['white']}{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{color}{design[-1]}{utils.COLOR_CODES['white']}")
        # 67
        canvas.draw(result, self.x, self.y)

def draw_card_back(canvas, x, y):
    canvas.draw([
        f"{utils.COLOR_CODES['gray']}┌───────┐",
        f"│ <><>< │",
        f"│ ><><> │",
        f"│ <><>< │",
        f"│ ><><> │",
        f"│ <><>< │",
        f"└───────┘",
        f"         "
    ], x, y)

def border(canvas, color = "gray"):
    for x in range(round(canvas.width)):
        canvas.draw_pixel(x, 0, "═", color)
        canvas.draw_pixel(x, canvas.height - 1, "═", color)
    for y in range(round(canvas.height)):
        canvas.draw_pixel(0, y, "║", color)
        canvas.draw_pixel(canvas.width - 1, y, "║", color)
    canvas.draw_pixel(0, 0, "╔", color)
    canvas.draw_pixel(canvas.width, 0, "╗", color)
    canvas.draw_pixel(0, canvas.height, "╚", color)
    canvas.draw_pixel(canvas.width, canvas.height, "╝", color)