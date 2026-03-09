#
# play.py
#
# Author:
# Micha Wüthrich
#
# Note:
# Run this file to play the game.
#


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
import select

import poker

if os.name != "nt":
    import select
    import termios
    import tty

def post_json(host: str, path: str, data: dict) -> tuple[int, dict]:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url=host + path,
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

def get_json(host: str, path: str, headers: dict = None) -> tuple[int, dict]:
    req = urllib.request.Request(
        url=host + path,
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

def write_json_file(path: str, content):
    real_path = os.path.abspath(path)
    with open(real_path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

def read_json_file(path: str):
    try:
        real_path = os.path.abspath(path)
        with open(real_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return False

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

    if ch == b" ":
        return " "

    if ch in (b"\t",):
        return "TAB"

    if ch in (b"\x7f", b"\b"):
        return "BACKSPACE"

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

    try:
        char = ch.decode("utf-8")
    except UnicodeDecodeError:
        return "OTHER"

    if char.islower():
        return char

    if char.isupper():
        return char

    if char.isdigit():
        return char

    special_chars = {
        "!": "!", '"': '"', "#": "#", "$": "$", "%": "%", "&": "&", "'": "'",
        "(": "(", ")": ")", "*": "*", "+": "+", ",": ",", "-": "-", ".": ".",
        "/": "/", ":": ":", ";": ";", "<": "<", "=": "=", ">": ">", "?": "?",
        "@": "@", "[": "[", "\\": "\\", "]": "]", "^": "^", "_": "_", "`": "`",
        "{": "{", "|": "|","}": "}", "~": "~", "ä": "ä", "ö": "ö", "ü": "ü",
        "Ä": "Ä","Ö": "Ö", "Ü": "Ü"
    }

    if char in special_chars:
        return special_chars[char]

    return "OTHER"

class UI:
    def __init__(self):
        self.w = 78
        self.h = 26
        self.text: list[str] = []
        self.reset_text()
        self.fps = 10
        self.note = ""
        self.servers = {
            "Local Server": "http://127.0.0.1:6767"
        }
        self.current_server: int = 0
        
        self.username: str = "micha"
        self.password: str = "geheim"
    
    @property
    def current_host(self):
        return list(self.servers.values())[self.current_server]
    
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

    def true_len(text: str, return_diff: bool = False):
        minus = 0
        reader = ""
        for char in text:
            if char == "\x1b":
                reader = ""
            reader += char
            if reader in [c.value for c in list(UI.Color)]:
                minus += len(reader)
                reader = ""
        
        if return_diff:
            return minus
        else:
            return len(text) - minus

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

    def draw_object(self, *args, **kwargs):
        obj = UI.Object(*args, **kwargs)
        color = obj.color
        if color is None:
            color = UI.Color.WHITE
        
        for i, line in enumerate(obj.text):
            plus = UI.true_len(self.text[obj.y + i], True)

            self.text[obj.y + i] = (
                "".join(list(self.text[obj.y + i])[:obj.x + plus]) +
                color.value + line + self.Color.RESET.value +
                "".join(list(self.text[obj.y + i])[obj.x + plus + UI.true_len(line):])
            )

    def poker_logo(self, x, y, color):
        self.draw_object(
            ["Michjzuman's Terminal-"],
            x + 13, y, self.Color.GRAY
        )
        self.draw_object(
            [
                "    _____    ____     ___ ___    _______  _____ ",
                "   /  _  | /  __  \  /  //  /   /  ____/ /  _  |",
                "  /   __/ /  / /  / /     /    /  /__   /     / ",
                " /  /    /  /_/  / /  /\  \   /  /___  /  /| |  ",
                "/__/     \______/ /__/  \__\ /______/ /__/ |_|  "
            ],
            x, y + 1, color
        )

    def suit_logos(self, x, y, number):
        if number > 0:
            self.draw_object([
                " __  __ ",
                "|  \/  |",
                " \    / ",
                "   \/   "
            ], x, y, self.Color.RED)
            
        if number > 1:
            self.draw_object([
                "   __   ",
                " _(  )_ ",
                "(__  __)",
                "   ||   "
            ], x + 10, y, self.Color.YELLOW)
            
        if number > 2:
            self.draw_object([
                "   /\   ",
                "  /  \  ",
                "  \  /  ",
                "   \/   "
            ], x + 20, y, self.Color.MAGENTA)
            
        if number > 3:
            self.draw_object([
                "   /\   ",
                "  /  \  ",
                " (_  _) ",
                "   ||   "
            ], x + 30, y, self.Color.BLUE)

    def label(self, text, y, color = None):
        if color is None:
            color = UI.Color.WHITE
        self.draw_object(
            [text],
            round(self.w / 2 - len(text) / 2), y,
            color
        )

    def menu(self, pointer, options, color, y = 13, w = 30, selection = None):
        for i, option in enumerate(options):
            text = option + (" (current)" if i == selection else "")
            
            half = (w - 10 - UI.true_len(text)) / 2
            c = color if pointer == i else UI.Color.GRAY
            star = "*" if selection == i else " "
            center = f"{star} {' ' * math.floor(half)}{UI.Color.BOLD.value}{text}{UI.Color.RESET.value}{c.value}{' ' * math.ceil(half)} {star}"
            self.draw_object(
                [
                    f"╭{'─' * (w - 2)}╮",
                    f"""│  {center}  │""",
                    f"╰{'─' * (w - 2)}╯"
                ] if pointer == i else [
                    f" ╭{'┄' * (w - 4)}╮ ",
                    f""" ┊ {center} ┊ """,
                    f" ╰{'┄' * (w - 4)}╯ "
                ],
                round(self.w / 2 - w / 2), y + i * 3, c
            )
    
    def selector(self, pointer_x, pointer_y, options, y, w = 40):
        for i, option in enumerate(options):
            text = f"   {option}{' ' * (w - 20 - len(option))}"
            color = UI.Color.WHITE if i == pointer_y else UI.Color.GRAY
            red = UI.Color.RED.value + UI.Color.BOLD.value if 0 == pointer_x and i == pointer_y else UI.Color.GRAY.value
            green = UI.Color.GREEN.value + UI.Color.BOLD.value if 1 == pointer_x and i == pointer_y else UI.Color.RESET.value + UI.Color.GRAY.value
            self.draw_object(
                [
                    f"╭{'─' * (w - 2)}╮",
                    f"""│{' ' * len(text)}{red}  ┌───┐ {green} ┌───┐ {color.value}│""",
                               f"""│{text}{red}  │ N │ {green} │ Y │ {color.value}│""",
                    f"""│{' ' * len(text)}{red}  └───┘ {green} └───┘ {color.value}│""",
                    f"╰{'─' * (w - 2)}╯"
                ],
                round(self.w / 2 - w / 2), y + i * 5, color
            )
    
    def text_input(self, text: str, pointer: bool, y: int = 10, label: str = "", hidden: bool = False):
        w = 30
        content = (
            "*" * len(text[:(w - 5)])
            if hidden else
            (
                text[-(w - 5):]
                if pointer else
                text[:(w - 5)]
            )
        ) + ("┃" if pointer else "")
        box = [] if label == "" else [f" {label}"]
        box += [
            f"┌{'─' * (w - 2)}┐",
            f"│ {content}{' ' * (w - 4 - len(content))} │",
            f"└{'─' * (w - 2)}┘"
        ]
        self.draw_object(box, round(self.w / 2 - max(len(line) for line in box) / 2), y)
    
    def back_button(self):
        self.draw_object(["< ESC"], 2, 1, UI.Color.GRAY)
    
    
    
    def intro_view(self):
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
            
            logo_y = 12 - max(0, frame - 20) * 2
            self.poker_logo(round(self.w / 2) - 24, logo_y, UI.Color.YELLOW)

            glitch(self.text, 100 - frame * 10)
            
            self.draw()
            
            time.sleep(1 / self.fps)
            frame += 1
            
            if logo_y <= 4:
                break
    
    def table_view(self, id):
        self.note = "↑/↓: Move • ENTER/SPACE: Select • Q: Quit"
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                try:
                    status, data = get_json(self.current_host, "/get_tables")
                    tables = [
                        f"""{
                            UI.Color.STRIKETHROUGH.value if t['active'] else ''
                        }Table {t['id'] + 1}     {
                            '(playing)' if t['active'] else '(waiting)'
                        }   ({t['players']}/8)"""
                        for t in data["tables"]
                    ]
                    for t in data["tables"]:
                        if t["id"] == id:
                            table = t
                except TypeError:
                    return
                
                # community cards
                self.draw_object(poker.print_cards_in_line(
                    poker.Card.Back,
                    poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
                    poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
                    poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
                    poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
                    poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
                    print_it = False,
                    spacer = " "
                ), 5, 2, UI.Color.WHITE)
                
                # pool
                pool = "67*"
                self.draw_object([pool], 71 - round(len(pool) / 2), 5, UI.Color.GREEN)
                
                # my cards
                self.draw_object(poker.print_cards_in_line(
                    poker.Card(poker.Rank.KING, poker.Suit.HEARTS),
                    poker.Card(poker.Rank.JACK, poker.Suit.HEARTS),
                    print_it = False
                ), 5, 16, UI.Color.WHITE)
                
                # players list
                players_list = []
                for i, player in enumerate(table["info"]["players"]):
                    arrow = ">" if i == table["info"]["turn"] else " "
                    green = UI.Color.GREEN.value if player["is_in"] else ""
                    gray = "" if player["is_in"] else UI.Color.GRAY.value + UI.Color.STRIKETHROUGH.value
                    reset = UI.Color.RESET.value if player["is_in"] else UI.Color.GRAY.value
                    players_list.append(
                        f"{gray}{arrow} [{green}10*{reset}] {player['name']} {green}{player['money']}*"
                    )
                self.draw_object("\n\n".join(players_list).split("\n"), 45, 16)
                
                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    
                    elif key == "ESC":
                        return
    
    def join_table_view(self):
        self.note = "↑/↓: Move • ENTER/SPACE: Select • Q: Quit"
        
        pointer = 0
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                try:
                    status, data = get_json(self.current_host, "/get_tables")
                    tables = [
                        f"""{
                            UI.Color.STRIKETHROUGH.value if table['active'] else ''
                        }Table {table['id'] + 1}     {
                            '(playing)' if table['active'] else '(waiting)'
                        }   ({table['players']}/8)"""
                        for table in data["tables"]
                    ]
                except TypeError:
                    return
                
                self.label("Join Table", 5, UI.Color.GREEN)
                
                self.menu(pointer, tables, UI.Color.GREEN, y = 10, w = 40)
                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "UP":
                        pointer -= 1
                        pointer %= len(tables)
                        break
                    elif key == "DOWN":
                        pointer += 1
                        pointer %= len(tables)
                        break
                    elif key in [" ", "ENTER"]:
                        self.table_view(data["tables"][pointer]["id"])
                        break
                    elif key == "ESC":
                        return
    
    def server_list_view(self):
        self.current_server = self.picker(
            self.servers,
            UI.Color.CYAN,
            self.current_server,
            "Server List"
        )
    
    def minigames_view(self):
        pass
    
    def statistics_view(self):
        pass
    
    def settings_view(self):
        pass
    
    def home_view(self):
        self.note = "↑/↓: Move • ENTER/SPACE: Select • Q: Quit"
        pointer = 0
        options = {
            "Join Table": self.join_table_view,
            "Settings": self.settings_view,
            "Change Server": self.server_list_view
        }
        
        try:
            status, data = get_json(self.current_host, "/money")
            money = data["players"][self.username]
        except TypeError:
            money = None
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                if money is not None:
                    self.draw_object([f"{self.username} {UI.Color.GREEN.value}{money}*"], 2, 1)
                
                self.poker_logo(round(self.w / 2) - 24, 4, UI.Color.YELLOW)
                
                self.menu(pointer, options, UI.Color.YELLOW)
                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "UP":
                        pointer -= 1
                        pointer %= len(options)
                        break
                    elif key == "DOWN":
                        pointer += 1
                        pointer %= len(options)
                        break
                    elif key in ["ENTER", " "]:
                        list(options.values())[pointer]()
                        break
    
    def login_register_form_view(self, login):
        self.note = "↑/↓: Move • ENTER: Confirm • ^C: Quit"
        
        pointer = 0
        text_inputs = {
            "Username": "",
            "Password": ""
        }
        error = ""
        if not login:
            text_inputs["Confirm Password"] = ""
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                self.label("Login" if login else "Register", 6 if login else 4)
                self.label(error, 7 if login else 5, UI.Color.RED)
                
                for i, text_input in enumerate(text_inputs):
                    self.text_input(
                        text_inputs[text_input], pointer == i, (10 if login else 7) + 5 * i, text_input,
                        "Password" in text_input
                    )
                
                self.menu(pointer - len(text_inputs), ["Done"], UI.Color.CYAN, 21 if login else 23)
                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "QUIT"):
                        exit()
                    elif key == "ESC":
                        return
                    elif key == "UP":
                        pointer -= 1
                        pointer %= len(text_inputs) + 1
                        break
                    elif (key == "ENTER" and pointer >= len(text_inputs) - 1) or (key == " " and pointer == len(text_inputs)):
                        if not login and text_inputs["Password"] != text_inputs["Confirm Password"]:
                            error = "wrong confirmation password"
                            break
                        status, data = post_json(self.current_host, "/login" if login else "/register", {
                            "username": text_inputs["Username"],
                            "password": text_inputs["Password"]
                        })
                        print(status, data)
                        if data["ok"]:
                            self.username = text_inputs["Username"]
                            self.password = text_inputs["Password"]
                            return True
                        elif status == 0:
                            error = "the server seems to be down"
                        else:
                            if login:
                                error = "wrong username or password"
                            else:
                                error = "username is already taken"
                        break
                    elif key in ["DOWN", "ENTER", "TAB"]:
                        pointer += 1
                        pointer %= len(text_inputs) + 1
                        break
                    elif key == "BACKSPACE" and pointer < len(text_inputs):
                        text_inputs[list(text_inputs.keys())[pointer]] = (
                            text_inputs[list(text_inputs.keys())[pointer]][:-1]
                        )
                        break
                    elif (key.isalpha() or key.isdigit() or not key.isalnum()) and len(key) == 1 and pointer < len(text_inputs):
                        text_inputs[list(text_inputs.keys())[pointer]] += key
                        break
    
    def start_view(self):
        self.note = "↑/↓: Move • ENTER/SPACE: Select • Q: Quit"
        pointer = 0
        options = {
            "Login": True,
            "Register": False
        }
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.poker_logo(round(self.w / 2) - 24, 4, UI.Color.YELLOW)
                
                self.menu(pointer, options, UI.Color.YELLOW)
                
                self.draw()
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "UP":
                        pointer -= 1
                        pointer %= len(options)
                        break
                    elif key == "DOWN":
                        pointer += 1
                        pointer %= len(options)
                        break
                    elif key in ["ENTER", " "]:
                        if self.login_register_form_view(list(options.values())[pointer]):
                            return
                        break
    
    
    
    def run(self):
        try:
            #self.intro_view()
            self.start_view()
            self.home_view()
            
            #self.join_table_view()
            #self.table_view(0)
            #self.login_register_form_view()
            
        except KeyboardInterrupt:
            exit()



if __name__ == "__main__":
    
    def test_run():
        poker.print_cards_in_line(
            poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
            poker.Card(poker.Rank.KING, poker.Suit.CLUBS),
            poker.Card(poker.Rank.QUEEN, poker.Suit.SPADES),
            poker.Card(poker.Rank.JACK, poker.Suit.DIAMONDS)
        )
        
        host = "http://127.0.0.1:6767"
        
        status, data = post_json(host, "/register", {"username": "micha", "password": "geheim"})
        print(status, data)
        status, data = post_json(host, "/register", {"username": "hans", "password": "geheim"})
        print(status, data)
        
        status, data = post_json(host, "/login", {"username": "micha", "password": "geheim"})
        print(status, data)
        
        status, data = post_json(host, "/join_table", {"username": "micha", "password": "geheim", "table_id": 0})
        print(status, data)
        status, data = post_json(host, "/join_table", {"username": "hans", "password": "geheim", "table_id": 0})
        print(status, data)
        
        time.sleep(7)
        
        # --- PREFLOP --- ---
        
        # micha bets big blind
        status, data = post_json(host, "/do_move", {"move_type": "Bet", "amount": 2, "username": "micha", "password": "geheim", "table_id": 0})
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
    
    #test_run()
    
    ui = UI()
    ui.run()
    
    for color in list(UI.Color):
        print(color.value + "Hello World!" + UI.Color.RESET.value, color)
