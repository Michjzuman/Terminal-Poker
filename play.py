from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager
import json
import urllib.request
import urllib.error
import time
import sys
import os
import random
import math

import poker

if os.name != "nt":
    import select
    import termios
    import tty

BASE = "http://127.0.0.1:6767"

def post_json(path: str, data: dict) -> tuple[int, dict]:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url=BASE + path,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            payload = resp.read().decode("utf-8")
            return status, json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8")
        try:
            return e.code, json.loads(payload) if payload else {}
        except Exception:
            return e.code, {"detail": payload}
    except Exception as e:
        return 0, {"error": str(e)}

def get_json(path: str, headers: dict = None) -> tuple[int, dict]:
    req = urllib.request.Request(
        url=BASE + path,
        headers={
            "Accept": "application/json",
            **(headers or {})
        },
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            payload = resp.read().decode("utf-8")
            return status, json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8")
        try:
            return e.code, json.loads(payload) if payload else {}
        except Exception:
            return e.code, {"detail": payload}
    except Exception as e:
        return 0, {"error": str(e)}

@contextmanager
def cbreak_stdin():
    if os.name == "nt" or not sys.stdin.isatty():
        yield
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def read_key():
    if os.name != "nt" and sys.stdin.isatty():
        ch = os.read(sys.stdin.fileno(), 1)
    else:
        ch = sys.stdin.buffer.read(1)
    if not ch:
        return None

    if ch in (b"\r", b"\n"):
        return "ENTER"

    if ch in (b"q", b"Q"):
        return "QUIT"

    if ch in (b"w", b"W"):
        return "UP"

    if ch in (b"s", b"S"):
        return "DOWN"

    if ch in (b"1", b"2", b"3", b"4", b"5", b"6"):
        return ch.decode()

    if ch == b"\x1b":
        seq = b""
        if os.name != "nt" and sys.stdin.isatty():
            fd = sys.stdin.fileno()
            deadline = time.monotonic() + 0.2
            while len(seq) < 16:
                timeout = deadline - time.monotonic()
                if timeout <= 0:
                    break
                ready, _, _ = select.select([fd], [], [], timeout)
                if not ready:
                    break
                nxt = os.read(fd, 1)
                if not nxt:
                    break
                seq += nxt
                if nxt.isalpha() or nxt == b"~":
                    break
        else:
            seq = sys.stdin.buffer.read(2)

        if (seq.startswith(b"[") or seq.startswith(b"O")) and seq.endswith(b"A"):
            return "UP"
        if (seq.startswith(b"[") or seq.startswith(b"O")) and seq.endswith(b"B"):
            return "DOWN"
        if (seq.startswith(b"[") or seq.startswith(b"O")) and seq.endswith(b"C"):
            return "RIGHT"
        if (seq.startswith(b"[") or seq.startswith(b"O")) and seq.endswith(b"D"):
            return "LEFT"
        return "ESC"

    return "OTHER"

class UI:
    def __init__(self):
        self.w = 67
        self.h = 25
        self.text: list[str] = []
        self.reset_text()
        self.fps = 10
        self.home_options = [
            "Server List",
            "Minigames",
            "Statistics",
            "Settings",
        ]
        self.note = ""
    
    class Color(Enum):
        RESET = "\033[0m"
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        GRAY = "\033[90m"
        
        BRIGHT_RED = "\033[91m"
        BRIGHT_GREEN = "\033[92m"
        BRIGHT_YELLOW = "\033[93m"
        BRIGHT_BLUE = "\033[94m"
        BRIGHT_MAGENTA = "\033[95m"
        BRIGHT_CYAN = "\033[96m"
        BRIGHT_WHITE = "\033[97m"
        
        BLACK_BG = "\033[40m"
        RED_BG = "\033[41m"
        GREEN_BG = "\033[42m"
        YELLOW_BG = "\033[43m"
        BLUE_BG = "\033[44m"
        MAGENTA_BG = "\033[45m"
        CYAN_BG = "\033[46m"
        WHITE_BG = "\033[47m"
        
        GRAY_BG = "\033[100m"
        BRIGHT_RED_BG = "\033[101m"
        BRIGHT_GREEN_BG = "\033[102m"
        BRIGHT_YELLOW_BG = "\033[103m"
        BRIGHT_BLUE_BG = "\033[104m"
        BRIGHT_MAGENTA_BG = "\033[105m"
        BRIGHT_CYAN_BG = "\033[106m"
        BRIGHT_WHITE_BG = "\033[107m"
        
        BOLD = "\033[1m"
        DIM = "\033[2m"
        ITALIC = "\033[3m"
        UNDERLINE = "\033[4m"
        BLINK = "\033[5m"
        INVERT = "\033[7m"
        HIDDEN = "\033[8m"
        STRIKETHROUGH = "\033[9m"

    def clear_shell(self):
        os.system("clear; clear")

    def reset_text(self):
        self.text = (
            [f"╔{'═' * self.w}╗"] +
            [
                f"║{''.join([' ' for _ in range(self.w)])}║"
                for _ in range(self.h)
            ] +
            [f"╚{'═' * self.w}╝"]
        )

    def draw(self):
        self.clear_shell()
        print("\n".join(self.text))
        print(UI.Color.GRAY.value + self.note + UI.Color.RESET.value)

    @dataclass
    class Object:
        text: list[str]
        x: int
        y: int
        color: "UI.Color" = None

    def draw_object(self, obj: Object):
        color = obj.color
        if color is None:
            color = random.choice(
                [self.Color.RED, self.Color.BLUE, self.Color.MAGENTA, self.Color.YELLOW]
            )
        
        for i, line in enumerate(obj.text):
            plus = 0

            reader = ""
            for char in self.text[obj.y + i]:
                if char == "\x1b":
                    reader = ""
                reader += char
                if reader in [c.value for c in list(self.Color)]:
                    plus += len(reader)
                    reader = ""

            self.text[obj.y + i] = (
                "".join(list(self.text[obj.y + i])[:obj.x + plus]) +
                color.value + line + self.Color.RESET.value +
                "".join(list(self.text[obj.y + i])[obj.x + plus + len(line):])
            )

    def poker_logo(self, x, y):
        self.draw_object(UI.Object(
            ["Michjzuman's Terminal-"],
            x + 12, y, self.Color.GRAY
        ))
        self.draw_object(UI.Object(
            [
                "    _____    ____     ___ ___    _______  _____ ",
                "   /  _  | /  __  \  /  //  /   /  ____/ /  _  |",
                "  /   __/ /  / /  / /     /    /  /__   /     / ",
                " /  /    /  /_/  / /  /\  \   /  /___  /  /| |  ",
                "/__/     \______/ /__/  \__\ /______/ /__/ |_|  "
            ],
            x, y + 1, self.Color.YELLOW
        ))

    def suit_logos(self, x, y, number):
        if number > 0:
            self.draw_object(UI.Object([
                " __  __ ",
                "|  \/  |",
                " \    / ",
                "   \/   "
            ], x, y, self.Color.RED))
            
        if number > 1:
            self.draw_object(UI.Object([
                "   __   ",
                " _(  )_ ",
                "(__  __)",
                "   ||   "
            ], x + 10, y, self.Color.YELLOW))
            
        if number > 2:
            self.draw_object(UI.Object([
                "   /\   ",
                "  /  \  ",
                "  \  /  ",
                "   \/   "
            ], x + 20, y, self.Color.MAGENTA))
            
        if number > 3:
            self.draw_object(UI.Object([
                "   /\   ",
                "  /  \  ",
                " (_  _) ",
                "   ||   "
            ], x + 30, y, self.Color.BLUE))

    def intro(self):
        self.note = "Made by Michjzuman"
        
        def glitch(text, prob: int):
            chars = ".-@#*|!?"
            for y, line in enumerate(text):
                for x, char in enumerate(line):
                    if char == " " and random.random() < (prob / 100):
                        text[y] = text[y][:x] + random.choice(chars) + text[y][x + 1:]
        
        frame = 0
        while True:
            self.reset_text()
            
            self.suit_logos(round(self.w / 2) - 19, 7, (
                4 - max(0, frame - 14)
            ))
            
            logo_y = 13 - max(0, frame - 20)
            self.poker_logo(round(self.w / 2) - 24, logo_y)

            glitch(self.text, 100 - frame * 10)
            
            self.draw()
            
            time.sleep(1 / self.fps)
            frame += 1
            
            if logo_y <= 4:
                break
    
    def home(self):
        self.note = "↑/↓: Move • ENTER: Select • Q: Quit"
        menu_w = 30
        
        pointer = 0
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.poker_logo(round(self.w / 2) - 24, 4)

                for i, option in enumerate(self.home_options):
                    half = (menu_w - 8 - len(option)) / 2
                    point = '*' if pointer == i else ' '
                    self.draw_object(UI.Object(
                        [
                            " " * menu_w,
                            f""" {point} [{' ' * math.floor(half)}{option}{' ' * math.ceil(half)}] {point} """,
                            " " * menu_w
                        ],
                        round(self.w / 2 - menu_w / 2), 12 + i * 3,
                        UI.Color.BLUE_BG if pointer == i else UI.Color.GRAY
                    ))

                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "QUIT"):
                        return
                    if key == "UP":
                        pointer -= 1
                        pointer %= len(self.home_options)
                        break
                    elif key == "DOWN":
                        pointer += 1
                        pointer %= len(self.home_options)
                        break
    
    def run(self):
        self.intro()
        
        self.home()
                


if __name__ == "__main__":
    
    def test_run():
        poker.print_cards_in_line(
            poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
            poker.Card(poker.Rank.KING, poker.Suit.CLUBS),
            poker.Card(poker.Rank.QUEEN, poker.Suit.SPADES),
            poker.Card(poker.Rank.JACK, poker.Suit.DIAMONDS)
        )
        
        status, data = post_json("/register", {"username": "micha", "password": "geheim"})
        print(status, data)
        status, data = post_json("/register", {"username": "hans", "password": "geheim"})
        print(status, data)
        
        status, data = post_json("/login", {"username": "micha", "password": "geheim"})
        print(status, data)
        
        status, data = post_json("/join_table", {"username": "micha", "password": "geheim", "table_id": 0})
        print(status, data)
        status, data = post_json("/join_table", {"username": "hans", "password": "geheim", "table_id": 0})
        print(status, data)
        
        time.sleep(7)
        
        # --- PREFLOP --- ---
        
        # micha bets big blind
        status, data = post_json("/do_move", {"move_type": "Bet", "amount": 2, "username": "micha", "password": "geheim", "table_id": 0})
        print(status, data)
        
        # hans bets small blind
        
        # --- FLOP --- ---
        
        # micha checks
        
        # hans raises by 3
        
        # micha calls
        
        # --- TURN --- ---
        
        # micha raises by 10
        
        # hans raises by 2
        
        # micha calls
        
        # --- RIVER --- ---
        
        # micha raises by 10
        
        # hans calls
        
        # --- SHOWDOWN --- ---
        
        # micha reveals his cards
        
        # hans reveals his cards
    
    ui = UI()
    ui.run()
    
    for color in list(UI.Color):
        print(color.value + "Hello World!" + UI.Color.RESET.value, color)
