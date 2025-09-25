import math

import tools

def draw(c):
    w = math.floor(tools.terminal_width() / 12)
    for cards in [c[:w], c[w:2*w], c[2*w:3*w]]:
        res = []
        for card in cards:
            num = card[-1]
            kind = {
                "H": "♥",
                "C": "♣",
                "D": "♦",
                "S": "♠",
                "B": ""
            }[card[0]]
            color = {
                "H": tools.RED,
                "C": tools.PURPLE,
                "D": tools.YELLOW,
                "S": tools.BLUE,
                "B": tools.GRAY
            }[card[0]]

            text = []
            if num == "B":
                text = [
                    f"+-------+",
                    f"| <><>< |",
                    f"| ><><> |",
                    f"| <><>< |",
                    f"| ><><> |",
                    f"| <><>< |",
                    f"+-------+",
                    f"         "
                ]
            elif num == "K":
                text = [
                    f"+-------+",
                    f"|  www  |",
                    f"|  [{kind}]  |",
                    f"| _/_\_ |",
                    f"||+ † +||",
                    f"| - - - |",
                    f"+-------+",
                    f"   K {kind}   "
                ]
            elif num == "Q":
                text = [
                    f"+-------+",
                    f"|  www  |",
                    f"|  ({kind})  |",
                    f"| _)*(_ |",
                    f"|(~~V~~)|",
                    f"| - - - |",
                    f"+-------+",
                    f"   Q {kind}   "
                ]
            elif num == "J":
                text = [
                    f"+-------+",
                    f"|  ,=~  |",
                    f"|  [{kind}{'}'}  |",
                    f"| _/_\_ |",
                    f"||\ |:/||",
                    f"| - - - |",
                    f"+-------+",
                    f"   J {kind}   "
                ]
            else:
                text = [
                    f"+-------+",
                    f"| {kind if not num in ['A', '2', '3'] else ' '} {kind if num in ['2', '3'] else ' '} {kind if not num in ['A', '2', '3'] else ' '} |",
                    f"|   {kind if num in ['7', '8', '9', '1'] else ' '}   |",
                    f"| {kind if num in ['6', '7', '8', '9', '1'] else ' '} {kind if num in ['A', '3', '5'] else ' '} {kind if num in ['6', '7', '8', '9', '1'] else ' '} |",
                    f"| {kind if num in ['9', '1'] else ' '} {kind if num in ['8', '1'] else ' '} {kind if num in ['9', '1'] else ' '} |",
                    f"| {kind if not num in ['A', '2', '3'] else ' '} {kind if num in ['2', '3'] else ' '} {kind if not num in ['A', '2', '3'] else ' '} |",
                    f"+-------+",
                    f"  {'10' if num == '1' else ' ' + num[-1]} {kind}   "
                ]

            for i in range(len(text)):
                if not i in [0, 6]:
                    text[i] = text[i][0] + color + text[i][1:-1] + tools.RESET + text[i][-1]

            res.append(text)
        if not res or not res[0]:
            return
        r = []
        for i in range(len(res[0])):
            line = []
            for card in res:
                line.append(card[i])
            r.append("   ".join(line))
        print("\n".join(r) + "\n")

if __name__ == "__main__":
    draw(["H3", "DQ", "S9", "CK", "H7", "DJ", "S2"])