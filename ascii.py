import math
import re

import tools
import animations


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def cards(c):
    result = []
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
                "H": tools.COLORS["red"],
                "C": tools.COLORS["purple"],
                "D": tools.COLORS["yellow"],
                "S": tools.COLORS["blue"],
                "B": tools.COLORS["gray"]
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
                    text[i] = text[i][0] + color + text[i][1:-1] + tools.COLORS["reset"] + text[i][-1]

            res.append(text)
        if not res or not res[0]:
            return "\n".join(result)
        r = []
        for i in range(len(res[0])):
            line = []
            for card in res:
                line.append(card[i])
            r.append("  ".join(line))
        result.append("\n".join(r))
    return "\n".join(result)

def _visible_len(s: str) -> int:
    """Length of s without ANSI escape sequences."""
    return len(ANSI_RE.sub("", s))

def _clip_ansi(s: str, width: int) -> str:
    """Clip string s to a visible width, preserving ANSI codes and not
    counting them toward width. Ensures a reset at the end."""
    out = []
    vis = 0
    i = 0
    while i < len(s) and vis < width:
        if s[i] == "\x1b" and i + 1 < len(s) and s[i + 1] == "[":
            j = i + 2
            while j < len(s) and s[j] != "m":
                j += 1
            if j < len(s):
                out.append(s[i : j + 1])
                i = j + 1
                continue
            else:
                # broken escape; stop consuming
                break
        else:
            out.append(s[i])
            vis += 1
            i += 1
    # ensure colors do not bleed beyond the clipped content
    out.append(tools.COLORS["reset"])
    return "".join(out)

def window(inner, keys=False):
    END = "+-------------------------------------------------------+"
    EMPTY = "|                                                       |"

    interior = len(EMPTY) - 2
    left_pad = 1
    content_width = interior - (left_pad * 2)

    MIN_LINES = 17
    raw_lines = inner.split("\n") if inner else [""]

    result_lines = []
    for raw_line in raw_lines:
        # clip to visible width while preserving ANSI codes
        clipped = _clip_ansi(raw_line, content_width)
        # compute visible length to pad the rest with plain spaces
        vis_len = _visible_len(clipped)
        if vis_len < content_width:
            clipped = clipped + (" " * (content_width - vis_len))
        # assemble the window line
        line_out = "|" + (" " * left_pad) + clipped + (" " * left_pad) + "|"
        result_lines.append(line_out)

    while len(result_lines) < MIN_LINES:
        blank = " " * content_width
        line_out = "|" + (" " * left_pad) + blank + (" " * left_pad) + "|"
        result_lines.append(line_out)

    result = "\n".join(result_lines)
    
    if keys:
        # Build colored labels first
        labels = []
        for key in keys:
            color = tools.COLORS.get(key.get("color", ""), "")
            reset = tools.COLORS["reset"] if color else ""
            label = f"{color}[{key['key'].upper()}] {key['action']}{reset}"
            labels.append(label)

        # Compute desired anchor positions across the content width
        n = len(labels)
        positions = []
        if n == 1:
            positions = [content_width // 2]
        else:
            # even spacing across [0, content_width-1]
            positions = [round(i * (content_width - 1) / (n - 1)) for i in range(n)]

        # Turn anchors into start indices based on visible lengths
        starts = []
        lens = [_visible_len(s) for s in labels]
        for i in range(n):
            half = lens[i] // 2
            start = positions[i] - half
            if start < 0:
                start = 0
            if start > content_width - lens[i]:
                start = max(0, content_width - lens[i])
            starts.append(start)

        # Resolve overlaps with a forward pass (left to right)
        for i in range(1, n):
            min_start = starts[i - 1] + lens[i - 1] + 1
            if starts[i] < min_start:
                starts[i] = min_start
                if starts[i] > content_width - lens[i]:
                    starts[i] = max(0, content_width - lens[i])

        # And a backward pass (right to left) for tight fits
        for i in range(n - 2, -1, -1):
            max_start = starts[i + 1] - lens[i] - 1
            if starts[i] > max_start:
                starts[i] = max(0, max_start)

        # Compute separator positions between labels (visible '|' dividers)
        seps = set()
        if n > 1:
            ends = [starts[i] + lens[i] - 1 for i in range(n)]
            for i in range(n - 1):
                mid = (ends[i] + starts[i + 1]) // 2
                # keep the separator outside labels
                if mid <= ends[i]:
                    mid = ends[i] + 1
                if mid >= starts[i + 1]:
                    mid = max(ends[i] + 1, min(starts[i + 1] - 1, mid))
                if 0 <= mid < content_width:
                    seps.add(mid)

        # Build the content line by visible cursor walking; insert labels at starts
        start_map = {starts[i]: labels[i] for i in range(n) if lens[i] > 0 and starts[i] >= 0}
        content_out = []
        vis_cursor = 0
        while vis_cursor < content_width:
            if vis_cursor in start_map:
                s = start_map[vis_cursor]
                content_out.append(s)
                vis_cursor += _visible_len(s)
            elif vis_cursor in seps:
                content_out.append("|")
                vis_cursor += 1
            else:
                content_out.append(" ")
                vis_cursor += 1
        # Ensure final reset (avoid color bleed)
        content_str = "".join(content_out) + tools.COLORS["reset"]

        # Assemble the keys line inside the same frame width
        keys_line = "|" + (" " * left_pad) + content_str + (" " * left_pad) + "|"
        return f"{END}\n{result}\n{END}\n{keys_line}\n{END}"
    else:
        return f"{END}\n{result}\n{END}"

if __name__ == "__main__":
    animations.intro()
    tools.clear()
    print(window(
        f"""Public Cards:\n{cards(["H3", "DQ", "S9", "CK", "H7"])}\n\nYour Cards:\n{cards(["CK", "H7"])}""",
        [
            {
                "key": "b",
                "action": "Bet",
                "color": "green"
            },
            {
                "key": "f",
                "action": "Fold",
                "color": "red"
            },
            {
                "key": "a",
                "action": "Test"
            }
        ]
    ))