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

HOST_FILE = ".current-host.json"

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

def normalize_host(host: str):
    if not host:
        return ""
    if host.startswith("http://") or host.startswith("https://"):
        return host.rstrip("/")
    return f"http://{host.rstrip('/')}"

def response_error_message(status: int, data: dict, fallback: str):
    if status == 0:
        return data.get("error") or fallback

    detail = data.get("detail") or data.get("message") or data.get("error")
    if detail:
        return f"{fallback}: {detail}"

    if status >= 400:
        return f"{fallback} (HTTP {status})"

    return fallback

def post_json(host: str, path: str, data: dict) -> tuple[int, dict]:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url=normalize_host(host) + path,
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
        url=normalize_host(host) + path,
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

def check_server(host: str):
    host = normalize_host(host)
    if not host or host.endswith("."):
        return False
    try:
        status, data = get_json(host, "/")
        return data["poker"] if data.get("ok") else False
    except Exception:
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
        self.current_host = ""
        
        self.settings: Settings = Settings()
        
        self.username: str = ""
        self.password: str = ""

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

    def api_error(self, status: int, data: dict, fallback: str):
        return response_error_message(status, data, fallback)

    def parse_card(self, raw_card):
        if isinstance(raw_card, poker.Card):
            return raw_card
        if not isinstance(raw_card, dict):
            return None

        try:
            return poker.Card(
                poker.Rank(raw_card["rank"]),
                poker.Suit(raw_card["suit"])
            )
        except (KeyError, ValueError, TypeError):
            return None

    def cards_from_payload(self, raw_cards):
        cards = []
        for raw_card in raw_cards or []:
            card = self.parse_card(raw_card)
            if card is not None:
                cards.append(card)
        return cards

    def cards_text(self, raw_cards):
        cards = self.cards_from_payload(raw_cards)
        if not cards:
            return ""
        return " ".join(
            f"{card.rank.value}{card.suit.symbol}"
            for card in cards
        )

    def hand_text(self, hand_data):
        if hand_data is None:
            return ""
        if isinstance(hand_data, str):
            return hand_data
        if isinstance(hand_data, (list, tuple)):
            if hand_data and isinstance(hand_data[0], dict):
                cards_text = self.cards_text(hand_data)
                if cards_text:
                    return cards_text
            return ", ".join(str(part) for part in hand_data)
        if isinstance(hand_data, dict):
            pieces = []
            for key in ["name", "rank", "label", "type"]:
                if hand_data.get(key):
                    pieces.append(str(hand_data[key]))
                    break
            cards_text = self.cards_text(
                hand_data.get("cards")
                or hand_data.get("best_cards")
                or hand_data.get("hand_cards")
            )
            if cards_text:
                pieces.append(cards_text)
            if hand_data.get("tiebreaker") is not None:
                pieces.append(str(hand_data["tiebreaker"]))
            if hand_data.get("points") is not None and not pieces:
                pieces.append(str(hand_data["points"]))
            return " | ".join(pieces) if pieces else str(hand_data)
        return str(hand_data)

    def player_name_from_ref(self, ref, players: list[dict]):
        if isinstance(ref, int):
            if 0 <= ref < len(players):
                player = players[ref]
                if isinstance(player, dict):
                    return player.get("name", str(ref))
                return getattr(player, "name", str(ref))
            return str(ref)
        if isinstance(ref, dict):
            return (
                ref.get("name")
                or ref.get("player")
                or ref.get("username")
                or str(ref)
            )
        return str(ref)

    def table_status_label(self, table: dict):
        info = table.get("info", {}) if isinstance(table, dict) else {}
        if info.get("ended"):
            return "(result)"
        if table.get("active"):
            return "(playing)"
        return "(waiting)"

    def flash_message(self, message: str, color=None, note: str = "", duration: float = 1.0):
        if color is None:
            color = UI.Color.YELLOW
        self.reset_text()
        self.label(message, 13, color)
        if note:
            self.draw(note)
        else:
            self.draw(" ")
        time.sleep(duration)

    def fetch_bankroll(self):
        status, data = get_json(self.current_host, "/money")
        if status != 200 or not data.get("ok"):
            return None, self.api_error(status, data, "could not load bankroll")

        players = data.get("players", {})
        if self.username not in players:
            return None, "bankroll unavailable"

        return players[self.username], ""

    def leave_table_request(self, table_id: int):
        status, data = post_json(self.current_host, "/leave_table", {
            "username": self.username,
            "password": self.password,
            "table_id": table_id
        })

        if data.get("ok"):
            return True, ""

        if status in (404, 405):
            return True, "leave-table is not available on this server yet"

        return False, self.api_error(status, data, "could not leave table")

    def payout_lines(self, payouts, players=None):
        players = players or []
        lines = []
        for payout in payouts or []:
            if isinstance(payout, dict):
                player_ref = payout.get("player") or payout.get("winner") or payout.get("name")
                amount = payout.get("amount")
            elif isinstance(payout, (list, tuple)) and len(payout) >= 2:
                player_ref = payout[0]
                amount = payout[1]
            else:
                player_ref = str(payout)
                amount = None

            name = self.player_name_from_ref(player_ref, players)
            if amount is None:
                lines.append(str(payout))
            else:
                lines.append(f"{name} +{amount}*")
        return lines

    def round_over_lines(self, info: dict):
        players = info.get("players", [])
        lines = []

        winner_names = info.get("winner_names", [])
        winners = (
            winner_names if len(winner_names) > 0 else
            [
                self.player_name_from_ref(winner, players)
                for winner in info.get("winner", [])
                if winner is not None
            ]
        )
        if winners:
            lines.append("Winners: " + ", ".join(winners))

        winning_hand = self.hand_text(info.get("winning_hand"))
        if winning_hand:
            lines.append("Winning hand: " + winning_hand)

        pots = info.get("pots", [])
        if pots:
            for idx, pot in enumerate(pots, start=1):
                if not isinstance(pot, dict):
                    lines.append(f"Pot {idx}: {pot}")
                    continue

                pot_line = f"Pot {idx}: {pot.get('amount', 0)}*"
                lines.append(pot_line)

                pot_winners = pot.get("winners") or pot.get("winner") or []
                if not isinstance(pot_winners, list):
                    pot_winners = [pot_winners]
                pot_winner_names = [
                    self.player_name_from_ref(winner, players)
                    for winner in pot_winners
                    if winner is not None
                ]
                if pot_winner_names:
                    lines.append("  Winners: " + ", ".join(pot_winner_names))

                pot_hand = self.hand_text(pot.get("winning_hand"))
                if pot_hand:
                    lines.append("  Hand: " + pot_hand)

                pot_payouts = self.payout_lines(pot.get("payouts", []), players)
                if pot_payouts:
                    lines.append("  Payouts: " + ", ".join(pot_payouts))
        else:
            payout_lines = self.payout_lines(info.get("payouts", []), players)
            lines.extend(payout_lines if payout_lines else ["No payout"])

        return lines[:12]
    
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

    def menu(self, pointer, options, color, y = 13, w = 30, selection = None, disabled=None):
        disabled = set(disabled or [])
        for i, option in enumerate(options):
            is_disabled = i in disabled
            text = option + (" (current)" if i == selection else "")
            if is_disabled:
                text += " (disabled)"
            
            half = (w - 10 - UI.true_len(text)) / 2
            if is_disabled:
                c = UI.Color.GRAY
                prefix = "x"
                text_style = UI.Color.GRAY.value + UI.Color.STRIKETHROUGH.value
            else:
                c = color if pointer == i else UI.Color.GRAY
                prefix = "*" if selection == i else " "
                text_style = UI.Color.BOLD.value

            center = f"{prefix} {' ' * math.floor(half)}{text_style}{text}{UI.Color.RESET.value}{c.value}{' ' * math.ceil(half)} {prefix}"
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
    
    def text_input(self, text: str, pointer: bool, y: int = 10, label: str = "", hidden: bool = False, placeholder: str = ""):
        w = 30
        content = (
            (
                "•" * len(text[:(w - 5)])
                if hidden else
                (
                    text[-(w - 5):]
                    if pointer else
                    text[:(w - 5)]
                )
            )
            if len(text) > 0 else
            UI.Color.GRAY.value + placeholder + UI.Color.RESET.value
        ) + ("┃" if pointer else "")
        box = [] if label == "" else [f" {label}"]
        box += [
            f"┌{'─' * (w - 2)}┐",
            f"│ {content}{' ' * (w - 4 - UI.true_len(content))} │",
            f"└{'─' * (w - 2)}┘"
        ]
        self.draw_object(box, round(self.w / 2 - max(UI.true_len(line) for line in box) / 2), y)
    
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
        
        pointer_x: int = 1
        amount: int = 5
        amount_input: bool = False
        
        cards_hidden = False
        
        key_pressed = False
        old_table = {}
        old_status_text = ""
        
        table = {}
        me = {}
        possible_moves = []
        status_text = ""
        status_color = UI.Color.RED
        
        my_cards = []
        my_turn: bool = False
        force_not_my_turn: bool = False
        
        zen_mode = False
        
        with cbreak_stdin():
            while True:
                now = time.monotonic()
                
                if now >= next_refresh:
                    try:
                        status, data = get_json(self.current_host, "/get_tables")
                        if not data.get("ok"):
                            status_text = self.api_error(status, data, "could not refresh table")
                            status_color = UI.Color.RED
                        else:
                            selected_table = next((t for t in data.get("tables", []) if t["id"] == id), None)
                            if selected_table is None:
                                self.flash_message("table not found", UI.Color.RED, "Returning to table list...")
                                return True
                            if not selected_table["active"]:
                                return self.table_lobby_view(id)
                            if selected_table["info"].get("ended"):
                                return self.podium_view(id)

                            table = selected_table
                            status_text = ""
                            status_color = UI.Color.RED
                            me = {}
                            possible_moves = []
                            my_turn = False

                            bankroll, bankroll_error = self.fetch_bankroll()
                            if bankroll_error:
                                status_text = bankroll_error
                                status_color = UI.Color.RED

                            players = table["info"].get("players", [])
                            for i, player in enumerate(players):
                                if player["name"] == self.username:
                                    me = player
                                    possible_moves = player.get("possible_moves", [])
                                    if player.get("is_turn") or table["info"].get("turn") == i:
                                        if not my_turn:
                                            force_not_my_turn = False
                                        my_turn = True
                                    break

                            if "phase" in list(table["info"].keys()) and last_phase != table["info"]["phase"]:
                                my_cards_status, my_cards_data = post_json(self.current_host, "/my_cards", {
                                    "username": self.username,
                                    "password": self.password,
                                    "table_id": id
                                })
                                if my_cards_data.get("ok"):
                                    my_cards = my_cards_data.get("cards", [])
                                else:
                                    status_text = self.api_error(my_cards_status, my_cards_data, "could not load your cards")
                                    status_color = UI.Color.RED
                                last_phase = table["info"]["phase"]

                            handshake_status, handshake_data = post_json(self.current_host, "/handshake", {
                                "username": self.username,
                                "password": self.password,
                                "table_id": id
                            })
                            if not handshake_data.get("ok"):
                                status_text = self.api_error(handshake_status, handshake_data, "could not keep table session alive")
                                status_color = UI.Color.RED
                    
                    except Exception as error:
                        status_text = str(error)
                        status_color = UI.Color.RED
                    
                    next_refresh = now + 0.5
                
                pointer_x %= max(1, len(possible_moves))
                
                if old_table != table or key_pressed or old_status_text != status_text:
                    key_pressed = False
                    old_table = table
                    old_status_text = status_text
                    
                    self.reset_text()
                    
                    if table != {}:
                        info = table["info"]
                        to_call = me.get("to_call", max(0, info.get("bet", 0) - me.get("bet", 0)))
                        minimum_raise_amount = me.get("minimum_raise_amount", 0)
                        maximum_raise_amount = me.get("maximum_raise_amount", 0)

                        bankroll, bankroll_error = self.fetch_bankroll()
                        if bankroll is not None:
                            self.draw_object([f"{self.username} {UI.Color.GREEN.value}{bankroll}*"], 2, 1)
                        elif bankroll_error:
                            self.draw_object([bankroll_error], 2, 1, UI.Color.RED)
                    
                        # === phase label ====================================
                        
                        self.draw_object([
                            table["info"]["phase"]
                        ], 6, 2, UI.Color.GRAY)
                        
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
                        ), 5, 3, UI.Color.WHITE)
                        
                        # === pool ===========================================
                        
                        pool_value = table['info']['pool']
                        if pool_value > 0:
                            pool = f"{pool_value}*"
                            self.draw_object([pool], 71 - round(len(pool) / 2), 5, UI.Color.GREEN)

                        info_line = (
                            f"To call: {to_call}*   "
                            f"Min raise: {minimum_raise_amount}*   "
                            f"Stack: {me.get('money', 0)}*"
                        )
                        if me.get("is_all_in"):
                            info_line += "   ALL-IN"
                        self.draw_object([info_line], 5, 14, UI.Color.CYAN)
                        
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
                            if amount_input:
                                minimum_amount = max(1, minimum_raise_amount)
                                maximum_amount = max(minimum_amount, maximum_raise_amount)
                                self.draw_object(
                                    ["".join([
                                        UI.Color.GRAY.value,
                                        "↑/↓ • Amount to ",
                                        possible_moves[pointer_x].lower(), ": ",
                                        UI.Color.GREEN.value,
                                        str(amount), "*", (
                                            "".join([
                                                UI.Color.GRAY.value,
                                                " (All In",
                                                *([
                                                    ": ", UI.Color.GREEN.value,
                                                    str(me["money"]), "*",
                                                    UI.Color.GRAY.value
                                                ] if amount > me["money"] else []),
                                                ")"
                                            ])
                                            if amount >= me["money"] else ''
                                        ), (
                                            "".join([
                                                UI.Color.GRAY.value,
                                                " (At Least: ",
                                                UI.Color.GREEN.value,
                                                f"{minimum_amount}*",
                                                UI.Color.GRAY.value,
                                                ", Max: ",
                                                UI.Color.GREEN.value,
                                                f"{maximum_amount}*",
                                                UI.Color.GRAY.value,
                                                ")"
                                            ])
                                            if amount < minimum_amount or amount > maximum_amount else ''
                                        )
                                    ])],
                                    5, 25
                                )
                            else:
                                action_labels = []
                                for move in possible_moves:
                                    label = move
                                    if move == "Call":
                                        cost = to_call
                                        if me.get("money", 0) <= cost:
                                            label += " (all-in)"
                                        else:
                                            label += f" (cost {cost}*)"
                                    elif move in ["Raise", "Re-Raise", "Bet"]:
                                        label += f" (min {max(1, minimum_raise_amount)}*)"
                                    action_labels.append(label)

                                if len(action_labels) > 0:
                                    for i, move in enumerate(action_labels):
                                        self.draw_object(
                                            ["".join([
                                                *([
                                                    UI.Color.YELLOW.value, "["
                                                ] if pointer_x == i else [" "]),
                                                f"{move}",
                                                *(["]"] if pointer_x == i else [" "]),
                                                UI.Color.RESET.value
                                            ])],
                                            5 + sum([len(m) + 2 for m in action_labels[:i]]),
                                            25, UI.Color.WHITE
                                        )
                                else:
                                    self.draw_object(
                                        ["Waiting for your turn"],
                                        5, 25, UI.Color.GRAY
                                    )
                        else:
                            self.draw_object(
                                ["Waiting for your turn"],
                                5, 25, UI.Color.GRAY
                            )
                        
                        # === players list ===================================
                        
                        players_list = []
                        for i, player in enumerate(table["info"]["players"]):
                            arrow = ">" if i == table["info"]["turn"] else " "
                            green = UI.Color.GREEN.value if player["is_in"] else ""
                            gray = "" if player["is_in"] else UI.Color.GRAY.value + UI.Color.STRIKETHROUGH.value
                            reset = UI.Color.RESET.value if player["is_in"] else UI.Color.GRAY.value
                            highlight = UI.Color.CYAN.value if player["name"] == self.username else ""
                            cards = f' [{player["cards"]}]' if player["cards"] else ""
                            role_tags = []
                            if i == info.get("button_index"):
                                role_tags.append("BTN")
                            if i == info.get("small_blind_index"):
                                role_tags.append("SB")
                            if i == info.get("big_blind_index"):
                                role_tags.append("BB")
                            if player.get("is_all_in"):
                                role_tags.append("ALL-IN")
                            role_suffix = f" ({', '.join(role_tags)})" if role_tags else ""
                            players_list.append(
                                f"{gray}{arrow} [{green}{player['bet']}*{reset}] {highlight}{player['name']}{reset}{cards}{role_suffix} {green}{player['money']}*"
                            )
                        self.draw_object(("\n" * (2 if len(players_list) <= 5 else 1)).join(players_list).split("\n"), 28, 16)
                        
                        # === logs ===========================================
                        
                        logs = [
                            f"{UI.Color.RED.value}{i + 1}. {log}{UI.Color.RESET.value}"
                            for i, log in list(enumerate(table["info"]["logs"]))[-14:]
                        ]
                        self.draw_object(logs, 76 - max([UI.true_len(l) for l in logs] + [0]), max(11, 16 - max(0, len(logs) - 10)))
                        
                        # ====================================================
                    
                    footer_lines = []
                    if status_text:
                        footer_lines.append(status_color.value + status_text + UI.Color.RESET.value)
                    if table != {} and len(table["info"]["logs"]) > 0:
                        footer_lines.append("logs symbols: [ ->: bet | -> +: raise | -: Check | #: Call | X: Fold ]")
                    footer_lines.append("←/→: Move • ENTER/SPACE: Select • C: Show/Hide Cards • Q: Quit")
                    self.draw("" if zen_mode else "\n".join(footer_lines))
                
                key = read_key_nonblocking(1 / self.fps)
                
                if key in ("q", "Q"):
                    exit()
                elif key in ("z", "Z"):
                    key_pressed = True
                    zen_mode = not zen_mode
                elif not amount_input and key == "RIGHT":
                    key_pressed = True
                    pointer_x += 1
                elif not amount_input and key == "LEFT":
                    key_pressed = True
                    pointer_x -= 1
                elif not amount_input and key in [" ", "ENTER"] and my_turn and not force_not_my_turn:
                    key_pressed = True
                    if len(possible_moves) == 0:
                        status_text = "no legal moves are available"
                        status_color = UI.Color.RED
                    elif possible_moves[pointer_x] in ["Raise", "Re-Raise", "Bet"]:
                        amount = max(1, me.get("minimum_raise_amount", 1))
                        amount_input = True
                    else:
                        status, do_move_data = post_json(self.current_host, "/do_move", {
                            "username": self.username,
                            "password": self.password,
                            "table_id": id,
                            "move_type": possible_moves[pointer_x],
                            "amount": 0
                        })
                        if do_move_data.get("ok"):
                            status_text = ""
                            status_color = UI.Color.RED
                            force_not_my_turn = True
                        else:
                            status_text = self.api_error(status, do_move_data, "move rejected")
                            status_color = UI.Color.RED
                elif amount_input and key in [" ", "ENTER"] and my_turn and not force_not_my_turn:
                    key_pressed = True
                    try:
                        minimum_amount = max(1, me.get("minimum_raise_amount", 1))
                        maximum_amount = max(minimum_amount, me.get("maximum_raise_amount", minimum_amount))
                        status, do_move_data = post_json(self.current_host, "/do_move", {
                            "username": self.username,
                            "password": self.password,
                            "table_id": id,
                            "move_type": possible_moves[pointer_x],
                            "amount": max(minimum_amount, min(maximum_amount, int(amount)))
                        })
                        if do_move_data.get("ok"):
                            amount_input = False
                            status_text = ""
                            status_color = UI.Color.RED
                            force_not_my_turn = True
                        else:
                            status_text = self.api_error(status, do_move_data, "move rejected")
                            status_color = UI.Color.RED
                    except ValueError:
                        status_text = "amount must be a number"
                        status_color = UI.Color.RED
                elif amount_input and key == "ESC":
                    key_pressed = True
                    amount_input = False
                elif amount_input and key in ["UP", "RIGHT"]:
                    key_pressed = True
                    maximum_amount = max(1, me.get("maximum_raise_amount", 1))
                    amount = min(maximum_amount, amount + 1)
                elif amount_input and key in ["DOWN", "LEFT"]:
                    key_pressed = True
                    minimum_amount = max(1, me.get("minimum_raise_amount", 1))
                    amount = max(minimum_amount, amount - 1)
                elif key in ["h", "H", "c", "C"]:
                    key_pressed = True
                    cards_hidden = not cards_hidden
    
    def podium_view(self, id):
        next_refresh = 0.0
        table = {}
        old_table = {}
        status_text = ""
        status_color = UI.Color.RED
        old_status_text = ""
        
        with cbreak_stdin():
            while True:
                now = time.monotonic()
                
                if now >= next_refresh:
                    try:
                        status, data = get_json(self.current_host, "/get_tables")
                        if not data.get("ok"):
                            status_text = self.api_error(status, data, "could not refresh round result")
                            status_color = UI.Color.RED
                        else:
                            selected_table = next((t for t in data.get("tables", []) if t["id"] == id), None)
                            if selected_table is None:
                                self.flash_message("table not found", UI.Color.RED, "Returning to table list...")
                                return True
                            if not selected_table["active"]:
                                return self.table_lobby_view(id)
                            if not selected_table["info"].get("ended"):
                                return self.table_view(id)
                            table = selected_table

                            bankroll, bankroll_error = self.fetch_bankroll()
                            if bankroll_error:
                                status_text = bankroll_error
                                status_color = UI.Color.RED
                            else:
                                status_text = ""

                        handshake_status, handshake_data = post_json(self.current_host, "/handshake", {
                            "username": self.username,
                            "password": self.password,
                            "table_id": id
                        })
                        if not handshake_data.get("ok"):
                            status_text = self.api_error(handshake_status, handshake_data, "could not keep table session alive")
                            status_color = UI.Color.RED
                    
                    except Exception as error:
                        status_text = str(error)
                        status_color = UI.Color.RED
                    
                    next_refresh = now + 0.5
                
                if old_table != table or old_status_text != status_text:
                    old_table = table
                    old_status_text = status_text
                    
                    self.reset_text()
                    
                    if table != {}:
                        info = table["info"]
                        bankroll, bankroll_error = self.fetch_bankroll()
                        if bankroll is not None:
                            self.draw_object([f"{self.username} {UI.Color.GREEN.value}{bankroll}*"], 2, 1)
                        elif bankroll_error:
                            self.draw_object([bankroll_error], 2, 1, UI.Color.RED)
                        
                        self.label("Round Over", 2, UI.Color.YELLOW)
                        summary_lines = self.round_over_lines(info)
                        self.draw_object(summary_lines[:8], 5, 5, UI.Color.GREEN)
                        
                        self.draw_object(poker.print_cards_in_line(
                            poker.Card.Back,
                            *[
                                poker.Card(
                                    poker.Rank(card["rank"]),
                                    poker.Suit(card["suit"])
                                )
                                for card in info["community_cards"]
                            ],
                            print_it = False,
                            spacer = " ",
                            design_option = poker.Card.DesignOption(self.settings.card_design),
                            back_design_option = poker.Card.Back.DesignOption(self.settings.card_back_design)
                        ), 5, 11, UI.Color.WHITE)
                    
                    footer_lines = []
                    if status_text:
                        footer_lines.append(status_color.value + status_text + UI.Color.RESET.value)
                    footer_lines.append("Waiting for next round • ESC: Leave Table • Q: Quit")
                    self.draw("\n".join(footer_lines))
                
                key = read_key_nonblocking(1 / self.fps)
                
                if key in ("q", "Q"):
                    exit()
                elif key == "ESC":
                    left, message = self.leave_table_request(id)
                    if left:
                        if message:
                            self.flash_message(message, UI.Color.YELLOW, "Returning home...")
                        return True
                    status_text = message
                    status_color = UI.Color.RED
    
    def table_lobby_view(self, id):
        next_refresh = 0.0
        table = {}
        old_table = {}
        status_text = ""
        status_color = UI.Color.RED
        old_status_text = ""
        
        with cbreak_stdin():
            while True:
                now = time.monotonic()
                
                if now >= next_refresh:
                    try:
                        status, data = get_json(self.current_host, "/get_tables")
                        if not data.get("ok"):
                            status_text = self.api_error(status, data, "could not refresh lobby")
                            status_color = UI.Color.RED
                        else:
                            selected_table = next((t for t in data.get("tables", []) if t["id"] == id), None)
                            if selected_table is None:
                                self.flash_message("table not found", UI.Color.RED, "Returning to table list...")
                                return True
                            if selected_table["active"]:
                                if selected_table["info"].get("ended"):
                                    return self.podium_view(id)
                                return self.table_view(id)
                            table = selected_table
                            status_text = ""

                        bankroll, bankroll_error = self.fetch_bankroll()
                        if bankroll_error:
                            status_text = bankroll_error
                            status_color = UI.Color.RED

                        handshake_status, handshake_data = post_json(self.current_host, "/handshake", {
                            "username": self.username,
                            "password": self.password,
                            "table_id": id
                        })
                        if not handshake_data.get("ok"):
                            status_text = self.api_error(handshake_status, handshake_data, "could not keep lobby session alive")
                            status_color = UI.Color.RED
                    except Exception as error:
                        status_text = str(error)
                        status_color = UI.Color.RED
                    
                    next_refresh = now + 0.5
                
                if old_table != table or old_status_text != status_text:
                    old_table = table
                    old_status_text = status_text
                    self.reset_text()
                    
                    self.back_button()
                    
                    self.label("Countdown", 8, UI.Color.GRAY)
                    self.label(str(table.get('count_down', 0)), 10, UI.Color.YELLOW)
                    
                    self.label("Players", 14, UI.Color.GRAY)
                    self.label(str(table.get("players", 0)), 16, UI.Color.CYAN)

                    bankroll, bankroll_error = self.fetch_bankroll()
                    if bankroll is not None:
                        self.draw_object([f"{self.username} {UI.Color.GREEN.value}{bankroll}*"], 2, 1)
                    elif bankroll_error:
                        self.draw_object([bankroll_error], 2, 1, UI.Color.RED)

                    footer_lines = []
                    if status_text:
                        footer_lines.append(status_color.value + status_text + UI.Color.RESET.value)
                    footer_lines.append("ESC: Leave Table • Q: Quit")
                    self.draw("\n".join(footer_lines))
                
                key = read_key_nonblocking(1 / self.fps)
                
                if key in ("q", "Q"):
                    exit()
                elif key == "ESC":
                    left, message = self.leave_table_request(id)
                    if left:
                        if message:
                            self.flash_message(message, UI.Color.YELLOW, "Returning home...")
                        return True
                    status_text = message
                    status_color = UI.Color.RED
    
    def join_table_view(self):
        pointer = 0
        status_text = ""
        status_color = UI.Color.RED
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                self.back_button()
                
                try:
                    status, get_tables_data = get_json(self.current_host, "/get_tables")
                    if not get_tables_data.get("ok"):
                        status_text = self.api_error(status, get_tables_data, "could not load tables")
                        status_color = UI.Color.RED
                        tables = []
                        disabled = set()
                    else:
                        raw_tables = get_tables_data.get("tables", [])
                        tables = [
                            f"Table {table['id'] + 1}     {self.table_status_label(table)}   ({table['players']}/8)"
                            for table in raw_tables
                        ]
                        disabled = {
                            i for i, table in enumerate(raw_tables)
                            if table.get("active") or table.get("players", 0) >= 8
                        }
                        status_text = ""
                except Exception as error:
                    status_text = str(error)
                    status_color = UI.Color.RED
                    tables = []
                    disabled = set()

                bankroll, bankroll_error = self.fetch_bankroll()
                
                self.label("Join Table", 5, UI.Color.GREEN)

                if bankroll is not None:
                    self.draw_object([f"{self.username} {UI.Color.GREEN.value}{bankroll}*"], 2, 1)
                elif bankroll_error:
                    self.draw_object([bankroll_error], 2, 1, UI.Color.RED)

                if len(tables) > 0:
                    pointer %= len(tables)
                    self.menu(pointer, tables, UI.Color.GREEN, y = 10, w = 40, disabled=disabled)
                else:
                    self.label("No tables available", 12, UI.Color.GRAY)

                footer_lines = []
                if status_text:
                    footer_lines.append(status_color.value + status_text + UI.Color.RESET.value)
                footer_lines.append("↑/↓: Move • ENTER/SPACE: Select • R: Reload • ESC/Q: Back")
                self.draw("\n".join(footer_lines))
                
                while True:
                    key = read_key()
                    if key in (None, "q", "Q"):
                        exit()
                    if key == "UP":
                        if len(tables) == 0:
                            break
                        pointer -= 1
                        pointer %= len(tables)
                        break
                    elif key == "DOWN":
                        if len(tables) == 0:
                            break
                        pointer += 1
                        pointer %= len(tables)
                        break
                    elif key in (None, "r", "R"):
                        break
                    elif key in [" ", "ENTER"]:
                        if len(tables) == 0:
                            status_text = "no tables available"
                            status_color = UI.Color.RED
                            break
                        selected_table = get_tables_data.get("tables", [])[pointer]
                        if pointer in disabled:
                            if selected_table.get("active"):
                                status_text = "table is busy"
                            elif selected_table.get("players", 0) >= 8:
                                status_text = "table is full"
                            else:
                                status_text = "table cannot be joined right now"
                            status_color = UI.Color.RED
                            break

                        status, data = post_json(self.current_host, "/join_table", {
                            "username": self.username,
                            "password": self.password,
                            "table_id": selected_table["id"]
                        })
                        if data.get("ok"):
                            self.table_lobby_view(selected_table["id"])
                            return
                        status_text = self.api_error(status, data, "could not join table")
                        status_color = UI.Color.RED
                        break
                    elif key == "ESC":
                        return
    
    def change_server_view(self, first_time = True):
        pointer = 0
        text_input = ""
        menu_len = 3
        new_server_on = None
        
        with cbreak_stdin():
            while True:
                current_server_on = check_server(self.current_host)
                
                self.reset_text()
                
                if not first_time:
                    self.back_button()
                
                self.label("Choose Server" if first_time else "Change Server", 5, self.settings.home_screen_color)
                
                if self.current_host != "":
                    current_server_color = UI.Color.GREEN.value if current_server_on else UI.Color.RED.value
                    self.label(
                        f"current: {self.current_host.replace('http://', '')} {current_server_color}•",
                        7, UI.Color.GRAY
                    )
                
                self.text_input(text_input, pointer == 0, 10, "Server Host")
                
                if not new_server_on is None:
                    y = 14
                    if new_server_on:
                        self.label("server found!", y, UI.Color.GREEN)
                    else:
                        self.label("not found", y, UI.Color.RED)
                
                self.menu(pointer - 1, ["Check", "Done"], UI.Color.CYAN, 15)
                
                self.draw("↑/↓: Move • ENTER: Confirm • ^C: Quit")
                
                while True:
                    key = read_key()
                    if key == "ESC" and not first_time:
                        return
                    elif key == "UP":
                        pointer -= 1
                        pointer %= menu_len
                        break
                    elif key in ["ENTER", " "] and pointer > 0:
                        new_server_on = check_server(text_input)
                        if pointer == 2:
                            if new_server_on:
                                if "://" not in text_input:
                                    text_input = "http://" + text_input
                                self.current_host = text_input
                                write_json_file(HOST_FILE, {
                                    "host": self.current_host
                                })
                                return
                        break
                    elif key in ["DOWN", "ENTER", "TAB"]:
                        pointer += 1
                        pointer %= menu_len
                        break
                    elif key == "BACKSPACE" and pointer < menu_len:
                        text_input = text_input[:-1]
                        break
                    elif (key.isalpha() or key.isdigit() or not key.isalnum()) and len(key) == 1 and pointer == 0:
                        text_input += key
                        break
    
    def minigames_view(self):
        self.flash_message("minigames are disabled", UI.Color.GRAY, "Returning...", 0.8)
    
    def statistics_view(self):
        self.flash_message("statistics are disabled", UI.Color.GRAY, "Returning...", 0.8)
    
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
        options = [
            "Join Table",
            "(Minigames)",
            "Settings",
            "<-] Logout"
        ]
        disabled = {1}
        status_text = ""
        status_color = UI.Color.RED

        with cbreak_stdin():
            while True:
                money, money_error = self.fetch_bankroll()

                self.reset_text()
                
                if money is not None:
                    self.draw_object([f"{self.username} {UI.Color.GREEN.value}{money}*"], 2, 1)
                elif money_error:
                    self.draw_object([money_error], 2, 1, UI.Color.RED)
                
                self.poker_logo(round(self.w / 2) - 24, 4, self.settings.home_screen_color)
                
                self.menu(pointer, options, self.settings.home_screen_color, disabled=disabled)

                footer_lines = []
                if status_text:
                    footer_lines.append(status_color.value + status_text + UI.Color.RESET.value)
                footer_lines.append("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                self.draw("\n".join(footer_lines))
                
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
                        selected = options[pointer]
                        if selected == "<-] Logout":
                            return
                        if selected == "(Minigames)":
                            status_text = "minigames are disabled"
                            status_color = UI.Color.RED
                            break
                        if selected == "Join Table":
                            self.join_table_view()
                        elif selected == "Settings":
                            self.settings_view()
                        break
    
    def wait_for_registration_approval_view(self):
        money = None
        tick = 0
        error = ""
        
        with cbreak_stdin():
            while True:
                self.reset_text()
                
                if tick == 0:
                    try:
                        status, money_data = get_json(self.current_host, "/money")
                        if money_data.get("ok"):
                            money = money_data.get("players", {})
                            error = ""
                        else:
                            error = self.api_error(status, money_data, "could not load approval status")
                            money = {}
                    except Exception as exc:
                        error = str(exc)
                        money = {}
                        
                    try:
                        status, rr_data = get_json(self.current_host, "/register-requests")
                        if rr_data.get("ok"):
                            registration_requests = rr_data.get("register-requests", [])
                        else:
                            error = self.api_error(status, rr_data, "could not load approval status")
                            registration_requests = []
                    except Exception as exc:
                        error = str(exc)
                        registration_requests = []
                    
                    if self.username in list(money.keys()):
                        return True
                    elif self.username in list(registration_requests):
                        pass
                    else:
                        return False
                
                self.label("Waiting for server admin to accept your registration", 13)
                if error:
                    self.label(error, 14, UI.Color.RED)
                
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
                        if status == 409:
                            if " " in text_inputs["Username"]:
                                error = "username cannot contain spaces"
                            else:
                                error = "username is too long"
                            break
                        if data.get("ok"):
                            self.username = text_inputs["Username"]
                            self.password = text_inputs["Password"]
                            if login:
                                return True
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
                    "Register": False,
                    "Change Server": "change_server"
                }
                if update_state.available:
                    options["Update"] = "update"
                pointer %= len(options)
                
                server_on = check_server(self.current_host)
                
                self.poker_logo(round(self.w / 2) - 24, 4, self.settings.home_screen_color)
                
                if update_state.available:
                    commit_word = "commit" if update_state.behind == 1 else "commits"
                    self.label(f"{update_state.behind} new git {commit_word} available", 10, UI.Color.YELLOW)
                
                color = UI.Color.GREEN.value if server_on else UI.Color.RED.value
                self.draw_object(
                    [f"{self.current_host.replace('http://', '')} {color}•"],
                    2, 1, UI.Color.GRAY
                )
                
                self.label(status_text, 11, status_color)
                
                self.menu(pointer, options, self.settings.home_screen_color)
                
                self.draw("↑/↓: Move • ENTER/SPACE: Select • Q: Quit")
                
                while True:
                    key = read_key()
                    if key in ("q", "Q"):
                        exit()
                    elif key in ("r", "R"):
                        break
                    elif key == "UP":
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
                        elif selected_action == "change_server":
                            self.change_server_view(False)
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
            host = read_json_file(HOST_FILE)
            if host and check_server(host["host"]):
                self.current_host = host["host"]
            else:
                self.change_server_view()
            #self.intro_view()
            self.start_view()
        
        except KeyboardInterrupt:
            exit()



if __name__ == "__main__":
    
    ui = UI()
    
    ui.run()
