import math

COLORS = {
    "red": "",
    "blue": "",
    "purple": "",
    "yellow": "",
    "gray": "",
    "green": "",
    "reset": ""
}
   
def card(rank: str = "7", suit: str = "H", selection: bool = False):
    color = {
        "H": COLORS["red"],
        "C": COLORS["purple"],
        "D": COLORS["yellow"],
        "S": COLORS["blue"],
        "B": COLORS["gray"]
    }[suit]
    s = {
        "H": "♥",
        "C": "♣",
        "D": "♦",
        "S": "♠",
        "B": ""
    }[suit]
    
    if rank == "K":
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
        result.append(f"{line[0]}{line[1:-1]}{line[-1]}")
        
    result += design[-2:]
    
    return result

def border(canvas):
    for x in range(round(canvas.width)):
        canvas.draw_pixel(x, 0, "═")
        canvas.draw_pixel(x, canvas.height - 1, "═")
    for y in range(round(canvas.height)):
        canvas.draw_pixel(0, y, "║")
        canvas.draw_pixel(canvas.width - 1, y, "║")
    canvas.draw_pixel(0, 0, "╔")
    canvas.draw_pixel(canvas.width, 0, "╗")
    canvas.draw_pixel(0, canvas.height, "╚")
    canvas.draw_pixel(canvas.width, canvas.height, "╝")