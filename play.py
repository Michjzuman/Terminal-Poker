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
import subprocess
import time
import sys
import os
import random
import math
import select

import poker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_project_dir():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return SCRIPT_DIR

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return SCRIPT_DIR

PROJECT_DIR = get_project_dir()
PLAY_SCRIPT_PATH = os.path.abspath(__file__)

if os.name != "nt":
    import select
    import termios
    import tty

@dataclass
class GitUpdateState:
    available: bool = False
    behind: int = 0

def resolve_project_path(path: str):
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_DIR, path)

def run_git_command(*args: str, timeout: int = 10):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
    except FileNotFoundError:
        return 127, "", "git is not installed"
    except subprocess.TimeoutExpired:
        return 124, "", "git command timed out"
    except OSError as e:
        return 1, "", str(e)

    return result.returncode, result.stdout.strip(), result.stderr.strip()

def last_output_line(stdout: str, stderr: str, fallback: str):
    for text in [stderr, stdout]:
        if text:
            return text.splitlines()[-1]
    return fallback

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
    real_path = resolve_project_path(path)
    with open(real_path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

def read_json_file(path: str):
    try:
        real_path = resolve_project_path(path)
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

def read_key_nonblocking(timeout: float = 0.0):
    if os.name != "nt" and sys.stdin.isatty():
        ready, _, _ = select.select([sys.stdin.fileno()], [], [], timeout)
        if not ready:
            return None
    return read_key()

class Settings:
    def __init__(self):
        self.card_design: poker.Card.DesignOption = (
            poker.Card.DesignOption.ROUND_DESIGN
        )
        self.card_back_design: poker.Card.Back.DesignOption = (
            poker.Card.Back.DesignOption.A
        )
        self.home_screen_color: "UI.Color" = UI.Color.YELLOW
        
        file = read_json_file(".poker-settings.json")
        if file != False:
            self.card_design = poker.Card.DesignOption(file["card_design"])
            self.card_back_design = poker.Card.Back.DesignOption(file["card_back_design"])
            self.home_screen_color = UI.Color(file["home_screen_color"])
    
    def save(self):
        write_json_file(".poker-settings.json", {
            "card_design": self.card_design.value,
            "card_back_design": self.card_back_design.value,
            "home_screen_color": self.home_screen_color.value
        })

class UI:
    def __init__(self):
        self.w = 78
        self.h = 26
        self.text: list[str] = []
        self.reset_text()
        self.fps = 10
        self.servers = {
            "Local Server": "http://127.0.0.1:6767"
        }
        self.current_server: int = 0
        
        self.settings: Settings = Settings()
        
        self.username: str = ""
        self.password: str = ""
    
    @property
    def current_host(self):
        return list(self.servers.values())[self.current_server]

    def git_update_state(self):
        code, stdout, _ = run_git_command("rev-parse", "--is-inside-work-tree")
        if code != 0 or stdout != "true":
            return GitUpdateState()

        code, _, _ = run_git_command(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
        )
        if code != 0:
            return GitUpdateState()

        run_git_command("fetch", "--quiet", timeout=15)

        code, stdout, _ = run_git_command(
            "rev-list", "--left-right", "--count", "HEAD...@{upstream}"
        )
        if code != 0:
            return GitUpdateState()

        counts = stdout.replace("\t", " ").split()
        if len(counts) != 2:
            return GitUpdateState()

        try:
            behind = int(counts[1])
        except ValueError:
            return GitUpdateState()

        return GitUpdateState(available=behind > 0, behind=behind)

    def pull_updates(self):
        code, stdout, stderr = run_git_command("pull", "--ff-only", timeout=30)
        if code != 0:
            return False, last_output_line(stdout, stderr, "git pull failed")
        return True, last_output_line(stdout, stderr, "update installed")

    def restart_application(self):
        os.execv(sys.executable, [sys.executable, PLAY_SCRIPT_PATH, *sys.argv[1:]])
    
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
        
        @property
        def normal(self) -> bool:
            if self in [
                UI.Color.RED,
                UI.Color.GREEN,
                UI.Color.YELLOW,
                UI.Color.BLUE,
                UI.Color.MAGENTA,
                UI.Color.CYAN,
                UI.Color.WHITE
            ]:
                return True
            return False

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

    def draw(self, note):
        self.clear_shell()
        print("\n".join(self.text))
        print(UI.Color.GRAY.value + note + UI.Color.RESET.value)

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
            
            if obj.y + i < self.h:
            
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
            "•" * len(text[:(w - 5)])
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
            self.poker_logo(round(self.w / 2) - 24, logo_y, self.settings.home_screen_color)

            glitch(self.text, 100 - frame * 10)
            
            self.draw("Made by Michjzuman")
            
            time.sleep(1 / self.fps)
            frame += 1
            
            if logo_y <= 4:
                break
    
    def table_view(self, id):
        next_refresh = 0.0
        last_phase = ""
        
        pointer_x = 1
        
        cards_hidden = False
        
        table = {}
        me = {}
        possible_moves = []
        
        my_cards = []
        my_turn: bool = False
        force_not_my_turn: bool = False
        
        with cbreak_stdin():
            while True:
                now = time.monotonic()
                
                if now >= next_refresh:
                    try:
                        _, data = get_json(self.current_host, "/get_tables")
                        if data.get("ok"):
                            for t in data["tables"]:
                                if t["id"] == id and t["active"]:
                                    table = t
                                    if "players" in list(t["info"].keys()):
                                        for i, player in enumerate(t["info"]["players"]):
                                            if player["name"] == self.username:
                                                me = player
                                                possible_moves = me["possible_moves"]
                                                if t["info"]["turn"] == i:
                                                    if not my_turn:
                                                        force_not_my_turn = False
                                                    my_turn = True
                                                else:
                                                    my_turn = False
                                                break
                            if "phase" in list(table["info"].keys()) and last_phase != table["info"]["phase"]:
                                _, my_cards_data = post_json(self.current_host, "/my_cards", {
                                    "username": self.username,
                                    "password": self.password,
                                    "table_id": id
                                })
                                if my_cards_data.get("ok"):
                                    my_cards = my_cards_data["cards"]
                                last_phase = table["info"]["phase"]
                    except TypeError or KeyError:
                        pass
                    
                    next_refresh = now + 0.5
                
                self.reset_text()
                
                if table != {}:
                
                    # === community cards ================================
                    
                    self.draw_object(poker.print_cards_in_line(
                        poker.Card.Back,
                        *[
                            poker.Card(
                                poker.Rank(card["rank"]),
                                poker.Suit(card["suit"])
                            )
                            for card in table["info"]["community_cards"]
                        ],
                        print_it = False,
                        spacer = " ",
                        design_option = poker.Card.DesignOption(self.settings.card_design),
                        back_design_option = poker.Card.Back.DesignOption(self.settings.card_back_design)
                    ), 5, 2, UI.Color.WHITE)
                    
                    # === pool ===========================================
                    
                    pool_value = table['info']['pool']
                    if pool_value > 0:
                        pool = f"{pool_value}*"
                        self.draw_object([pool], 71 - round(len(pool) / 2), 5, UI.Color.GREEN)
                    
                    # === my cards =======================================
                    
                    self.draw_object(poker.print_cards_in_line(
                        *[
                            poker.Card.Back
                            for _ in range(len(my_cards))
                        ] if cards_hidden else [
                            poker.Card(poker.Rank(card["rank"]), poker.Suit(card["suit"]))
                            for card in my_cards
                        ],
                        print_it = False,
                        design_option = poker.Card.DesignOption(self.settings.card_design),
                        back_design_option = poker.Card.Back.DesignOption(self.settings.card_back_design)
                    ), 5, 16, UI.Color.WHITE)
                    
                    # === possible moves =================================
                    
                    if my_turn and not force_not_my_turn:
                        for i, move in enumerate(possible_moves):
                            self.draw_object(
                                ["".join([
                                    UI.Color.YELLOW.value if pointer_x == i else "",
                                    "[" if pointer_x == i else " ",
                                    f"{move}",
                                    "]" if pointer_x == i else " ",
                                    UI.Color.RESET.value
                                ])],
                                5 + sum([len(m) + 2 for m in me["possible_moves"][:i]]),
                                25, UI.Color.WHITE
                            )
                    
                    # === logs ===========================================
                    
                    logs = [
                        f"{UI.Color.RED.value}{i + 1}. {log}{UI.Color.RESET.value}"
                        for i, log in list(enumerate(table["info"]["logs"]))[-15:]
                    ]
                    logs_x = 85 - max([UI.true_len(l) for l in logs] + [0])
                    self.draw_object(logs,logs_x, max(11, 16 - max(0, len(logs) - 10)))
                    
                    # === players list ===================================
                    
                    players_list = []
                    for i, player in enumerate(table["info"]["players"]):
                        arrow = ">" if i == table["info"]["turn"] else " "
                        green = UI.Color.GREEN.value if player["is_in"] else ""
                        gray = "" if player["is_in"] else UI.Color.GRAY.value + UI.Color.STRIKETHROUGH.value
                        reset = UI.Color.RESET.value if player["is_in"] else UI.Color.GRAY.value
                        highlight = UI.Color.CYAN.value if player["name"] == self.username else ""
                        players_list.append(
                            f"{gray}{arrow} [{green}{player['bet']}*{reset}] {highlight}{player['name']}{reset} {green}{player['money']}*"
                        )
                    players_list_x = logs_x - max([UI.true_len(p) for p in players_list] + [0]) - 3
                    self.draw_object(("\n" * (2 if len(players_list) <= 5 else 1)).join(players_list).split("\n"), players_list_x, 16)
                    
                    # ====================================================
                
                self.draw("←/→: Move • ENTER/SPACE: Select • H: Show/Hide Cards • Q: Quit")
                
                key = read_key_nonblocking(1 / self.fps)
                
                if key in ("q", "Q"):
                    exit()
                elif key == "RIGHT":
                    pointer_x += 1
                    pointer_x %= max(1, len(possible_moves))
                elif key == "LEFT":
                    pointer_x -= 1
                    pointer_x %= max(1, len(possible_moves))
                elif key in [" ", "ENTER"] and my_turn and not force_not_my_turn:
                    status, do_move_data = post_json(self.current_host, "/do_move", {
                        "username": self.username,
                        "password": self.password,
                        "table_id": id,
                        "move_type": possible_moves[pointer_x],
                        "amount": 5
                    })
                    if do_move_data.get("ok"):
                        force_not_my_turn = True
                elif key in ["h", "H", "c", "C"]:
                    cards_hidden = not cards_hidden
                elif key == "ESC":
                    return
    
    def table_lobby_view(self, id):
        next_refresh = 0.0
        
        cards_hidden = False
        
        with cbreak_stdin():
            while True:
                now = time.monotonic()
                
                if now >= next_refresh:
                    try:
                        _, data = get_json(self.current_host, "/get_tables")
                        if data.get("ok"):
                            for t in data["tables"]:
                                if t["id"] == id:
                                    if t["active"]:
                                        self.table_view(id)
                                        return
                                    else:
                                        table = t
                    except TypeError:
                        return
                    
                    next_refresh = now + 0.5
                
                self.reset_text()
                
                self.back_button()
                
                self.label("Countdown", 8, UI.Color.GRAY)
                self.label(str(table['count_down']), 10, UI.Color.YELLOW)
                
                self.label("Players", 14, UI.Color.GRAY)
                self.label(str(table["players"]), 16, UI.Color.CYAN)
                
                self.draw("Q: Quit")
                
                key = read_key_nonblocking(1 / self.fps)
                
                if key in ("q", "Q"):
                    exit()
                elif key == "ESC":
                    return
    
    def join_table_view(self):
        pointer = 0
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                try:
                    status, get_tables_data = get_json(self.current_host, "/get_tables")
                    tables = [
                        f"""{
                            UI.Color.STRIKETHROUGH.value if table['active'] else ''
                        }Table {table['id'] + 1}     {
                            '(playing)' if table['active'] else '(waiting)'
                        }   ({table['players']}/8)"""
                        for table in get_tables_data["tables"]
                    ]
                except TypeError:
                    return
                
                self.label("Join Table", 5, UI.Color.GREEN)
                
                self.menu(pointer, tables, UI.Color.GREEN, y = 10, w = 40)
                
                self.draw("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                
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
                        status, data = post_json(self.current_host, "/join_table",
                            {
                                "username": self.username,
                                "password": self.password,
                                "table_id": get_tables_data["tables"][pointer]["id"]
                            }
                        )
                        self.table_lobby_view(get_tables_data["tables"][pointer]["id"])
                        break
                    elif key == "ESC":
                        return
    
    def server_list_view(self):
        pass
    
    def minigames_view(self):
        pass
    
    def statistics_view(self):
        pass
    
    def settings_window_size_view(self):
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                self.label("Set Window Size", 4)
                
                self.draw("↑/↓/←/→: Resize • Q: Quit")
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "ESC":
                        return
                    elif key == "UP":
                        self.h -= 1
                        self.h = max(self.h, 26)
                        break
                    elif key == "DOWN":
                        self.h += 1
                        self.h = min(self.h, 54)
                        break
                    if key == "RIGHT":
                        self.w += 1
                        self.w = min(self.w, 200)
                        break
                    elif key == "LEFT":
                        self.w -= 1
                        self.w = max(self.w, 78)
                        break
    
    def settings_card_designs_view(self, back = False):
        options = list(
            poker.Card.Back.DesignOption
            if back else
            poker.Card.DesignOption
        )
        
        pointer = options.index(
            self.settings.card_back_design
            if back else
            self.settings.card_design
        )
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                self.label(f"Choose Your Card{' Back' if back else ''} Design", 4)
                
                self.label(options[pointer].value + " design", 10, UI.Color.GREEN)
                
                self.draw_object([
                    "╔═════════╗"
                ], 4 + 10 * pointer, 16, UI.Color.GREEN)
                
                for i, option in enumerate(options):
                    self.draw_object(
                        (
                            poker.Card.Back.ascii(option,
                                self.settings.card_design
                            )[:-1]
                            if back else
                            poker.Card(
                                poker.Rank.EIGHT,
                                poker.Suit.DIAMONDS
                            ).ascii(option)[:-1]
                        ),
                        5 + 10 * i, 17
                    )
                    
                self.draw_object([
                    "╚═════════╝"
                ], 4 + 10 * pointer, 24, UI.Color.GREEN)
                
                self.draw("←/→: Move • Q: Quit")
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    elif key == "RIGHT":
                        pointer += 1
                        pointer %= len(options)
                        break
                    elif key == "LEFT":
                        pointer -= 1
                        pointer %= len(options)
                        break
                    elif key in ["ENTER", " ", "ESC"]:
                        if back:
                            self.settings.card_back_design = options[pointer]
                        else:
                            self.settings.card_design = options[pointer]
                        return
    
    def settings_card_back_designs_view(self):
        self.settings_card_designs_view(True)
    
    def settings_home_screen_color_view(self):
        options = [color for color in list(UI.Color) if color.normal]
        
        pointer = options.index(self.settings.home_screen_color)
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                self.label("Choose Your Home Screen Color", 8, options[pointer])
                
                color_select_x = round(
                    self.w / 2 -
                    (len(options) * 10 - 4) / 2
                )
                
                self.draw_object([
                    "╔════════╗"
                ], color_select_x - 2 + 10 * pointer, 16, UI.Color.GREEN)
                
                for i, option in enumerate(options):
                    self.draw_object(
                        [
                            "██████",
                            "██████",
                            "██████"
                        ],
                        color_select_x + 10 * i, 17, option
                    )
                    
                self.draw_object([
                    "╚════════╝"
                ], color_select_x - 2 + 10 * pointer, 20, UI.Color.GREEN)
                
                self.draw("↑/↓: Move • Q: Quit")
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    elif key == "RIGHT":
                        pointer += 1
                        pointer %= len(options)
                        break
                    elif key == "LEFT":
                        pointer -= 1
                        pointer %= len(options)
                        break
                    elif key in ["ENTER", " ", "ESC"]:
                        self.settings.home_screen_color = options[pointer]
                        return
    
    def settings_view(self):
        pointer = 0
        options = {
            #"Window Size": self.settings_window_size_view,
            "Home Screen Color": self.settings_home_screen_color_view,
            "Card Designs": self.settings_card_designs_view,
            "Card Back Designs": self.settings_card_back_designs_view
        }
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                self.label("Settings", 4)
                
                self.menu(pointer, options, self.settings.home_screen_color, 8)
                
                self.draw("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "ESC":
                        return
                    elif key == "UP":
                        pointer -= 1
                        pointer %= len(options)
                        break
                    elif key == "DOWN":
                        pointer += 1
                        pointer %= len(options)
                        break
                    elif key in ["ENTER", " "]:
                        list(options.values())[pointer]()
                        self.settings.save()
                        break
    
    def home_view(self):
        pointer = 0
        options = {
            "Join Table": self.join_table_view,
            "(Minigames)": print,
            "Settings": self.settings_view,
            "<-] Logout": None
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
                
                self.poker_logo(round(self.w / 2) - 24, 4, self.settings.home_screen_color)
                
                self.menu(pointer, options, self.settings.home_screen_color)
                
                self.draw("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                
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
                        if "Logout" in list(options.keys())[pointer]:
                            return
                        list(options.values())[pointer]()
                        break
    
    def wait_for_registration_approval_view(self):
        money = None
        tick = 0
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                if tick == 0:
                    try:
                        status, money_data = get_json(self.current_host, "/money")
                        money = money_data["players"]
                    except TypeError:
                        money = {}
                        
                    try:
                        status, rr_data = get_json(self.current_host, "/register-requests")
                        registration_requests = rr_data["register-requests"]
                    except TypeError:
                        registration_requests = []
                    
                    if self.username in list(money.keys()):
                        return True
                    elif self.username in list(registration_requests):
                        pass
                    else:
                        return False
                
                self.label("Waiting for server admin to accept your registration", 13)
                
                self.label(["     ", ".    ", ". .  ", ". . ."][tick], 15)
                
                self.draw("^C: Quit")
                
                tick += 1
                tick %= 4
                
                time.sleep(1)
    
    def login_register_form_view(self, login):
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
                
                self.draw("↑/↓: Move • ENTER: Confirm • ^C: Quit")
                
                while True:
                    key = read_key()
                    if key == "ESC":
                        return
                    elif key == "UP":
                        pointer -= 1
                        pointer %= len(text_inputs) + 1
                        break
                    elif (key == "ENTER" and pointer >= len(text_inputs) - 1) or (key == " " and pointer == len(text_inputs)):
                        if "" in list(text_inputs.values()):
                            error = "not all values were given"
                            break
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
                            approved = self.wait_for_registration_approval_view()
                            return approved
                        elif status == 0:
                            error = "could not connect to server"
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
        pointer = 0
        update_state = self.git_update_state()
        restart_requested = False
        
        status_text = ""
        status_color = UI.Color.RED
        
        with cbreak_stdin():
            while True:
                self.reset_text()

                options = {
                    "Login": True,
                    "Register": False
                }
                if update_state.available:
                    options["Update"] = "update"
                pointer %= len(options)
                
                self.poker_logo(round(self.w / 2) - 24, 4, self.settings.home_screen_color)
                
                if update_state.available:
                    commit_word = "commit" if update_state.behind == 1 else "commits"
                    self.label(f"{update_state.behind} new git {commit_word} available", 10, UI.Color.YELLOW)
                
                self.label(status_text, 11, status_color)
                
                self.menu(pointer, options, self.settings.home_screen_color)
                
                self.draw("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                
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
                        selected_label = list(options.keys())[pointer]
                        selected_action = list(options.values())[pointer]
                        
                        if selected_action == "update":
                            success, message = self.pull_updates()
                            if success:
                                restart_requested = True
                                break
                            status_text = message
                            status_color = UI.Color.RED
                            update_state = self.git_update_state()
                        else:
                            login_result = self.login_register_form_view(selected_action)
                            if login_result:
                                self.home_view()
                                status_text = ""
                                update_state = self.git_update_state()
                            elif login_result is False and selected_label == "Register":
                                status_text = "your registration was rejected"
                                status_color = UI.Color.RED
                        break
                if restart_requested:
                    break
        
        if restart_requested:
            self.restart_application()
    
    
    
    def run(self):
        try:
            self.intro_view()
            self.start_view()
        
        except KeyboardInterrupt:
            exit()



if __name__ == "__main__":
    
    ui = UI()
    
    ui.run()
