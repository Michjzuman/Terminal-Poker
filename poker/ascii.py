import math

import utils
   
def card(rank: str = "7", suit: str = "", selection: bool = False):
    color = {
        "H": utils.COLORS["red"],
        "C": utils.COLORS["purple"],
        "D": utils.COLORS["yellow"],
        "S": utils.COLORS["blue"],
        "B": utils.COLORS["gray"]
    }[suit]
    s = {
        "H": "♥",
        "C": "♣",
        "D": "♦",
        "S": "♠",
        "B": ""
    }[suit]
    
    if rank == "B":
        design = [
            f"┌───────┐",
            f"│ <><>< │",
            f"│ ><><> │",
            f"│ <><>< │",
            f"│ ><><> │",
            f"│ <><>< │",
            f"└───────┘",
            f"         "
        ]
        for line in design:
            line = f"{utils.COLORS['green']}{design}{utils.COLORS['white']}"
        return design
    elif rank == "K":
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
    elif rank == "Q":
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
    elif rank == "J":
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
            f"│ {s if not rank in ['A', '2', '3'] else ' '} {s if rank in ['2', '3'] else ' '} {s if not rank in ['A', '2', '3'] else ' '} │",
            f"│   {s if rank in ['7', '8', '9', '10'] else ' '}   │",
            f"│ {s if rank in ['6', '7', '8', '9', '10'] else ' '} {s if rank in ['A', '3', '5'] else ' '} {s if rank in ['6', '7', '8', '9', '10'] else ' '} │",
            f"│ {s if rank in ['9', '10'] else ' '} {s if rank in ['8', '10'] else ' '} {s if rank in ['9', '10'] else ' '} │",
            f"│ {s if not rank in ['A', '2', '3'] else ' '} {s if rank in ['2', '3'] else ' '} {s if not rank in ['A', '2', '3'] else ' '} │",
            f"└───────┘",
            f"  {'10' if rank == '10' else ' ' + rank[-1]} {s}   "
        ]
    
    result = design[:1]
    
    for line in design[1:-2]:
        result.append(f"{line[0]}{color}{line[1:-1]}{utils.COLORS['white']}{line[-1]}")
        
    result += design[-2:-1]
    result.append(f"{color}{design[-1]}{utils.COLORS['white']}")
    
    return result

def border(canvas):
    color = "gray"
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

