from enum import Enum
import json
import urllib.request
import urllib.error
import time
import sys
import os
import random

import poker

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

def clear_shell():
    os.system("clear; clear")

def read_key():
    ch = sys.stdin.buffer.read(1)
    if not ch:
        return None

    if ch in (b"\r", b"\n"):
        return "ENTER"

    if ch in (b"q", b"Q"):
        return "QUIT"

    if ch in (b"1", b"2", b"3", b"4", b"5", b"6"):
        return ch.decode()

    if ch == b"\x1b":
        seq = sys.stdin.buffer.read(2)
        if seq == b"[A":
            return "UP"
        if seq == b"[B":
            return "DOWN"
        if seq == b"[C":
            return "RIGHT"
        if seq == b"[D":
            return "LEFT"
        return "ESC"

    return "OTHER"

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

def intro():
    w, h = 67, 25
    
    text = (
        [f"╔{'═' * w}╗"] +
        [
            f"║{''.join([' ' for _ in range(w)])}║"
            for _ in range(h)
        ] +
        [f"╚{'═' * w}╝"]
    )
    
    def addobject(obj, x, y, color = None):
        if color is None:
            color = random.choice(
                [Color.RED, Color.BLUE, Color.MAGENTA, Color.YELLOW]
            )
        
        for i, line in enumerate(obj):
            plus = 0

            reader = ""
            for char in text[y + i]:
                if char == "\x1b":
                    reader = ""
                reader += char
                if reader in [c.value for c in list(Color)]:
                    plus += len(reader)
                    reader = ""

            text[y + i] = (
                "".join(list(text[y + i])[:x + plus]) +
                color.value + line + Color.RESET.value +
                "".join(list(text[y + i])[x + plus + len(line):])
            )
    
    while True:
        clear_shell()
    
        addobject([
            " __  __ ",
            "|  \/  |",
            " \    / ",
            "   \/   "
        ], 4, 2)
        
        addobject([
            "   __   ",
            " _(  )_ ",
            "(__  __)",
            "   ||   "
        ], 14, 2)
        
        addobject([
            "   /\   ",
            "  /  \  ",
            "  \  /  ",
            "   \/   "
        ], 24, 2)
        
        addobject([
            "   /\   ",
            "  /  \  ",
            " (_  _) ",
            "   ||   "
        ], 34, 2)

        print("\n".join(text))
        time.sleep(0.1)
        break
        
    """
        
║                                                        ║
║  \033[31m   __  __   \033[34m      __      \033[33m     /\      \033[35m     /\     \033[0m   ║
║  \033[31m  |  \/  |  \033[34m    _(  )_    \033[33m    /  \     \033[35m    /  \    \033[0m   ║
║  \033[31m   \    /   \033[34m   (__  __)   \033[33m    \  /     \033[35m   (_  _)   \033[0m   ║
║  \033[31m     \/     \033[34m      ||      \033[33m     \/      \033[35m     ||     \033[0m   ║
║                                                        ║
║                                                        ║
║                                                        ║
║                 \033[90mMichjzuman's Terminal-\033[0m                 ║
║  {colors[0]}      _____ {colors[1]}   ____   {colors[2]}  ___ ___ {colors[3]}   _______ {colors[4]} _____    \033[0m ║
║  {colors[0]}     /  _  |{colors[1]} /  __  \ {colors[2]} /  //  / {colors[3]}  /  ____/{colors[4]} /  _  |   \033[0m ║
║  {colors[0]}    /   __/ {colors[1]}/  / /  /{colors[2]} /     /  {colors[3]}  /  /__ {colors[4]}  /     /    \033[0m ║
║  {colors[0]}   /  /    {colors[1]}/  /_/  /{colors[2]} /  /\  \ {colors[3]}  /  /___ {colors[4]} /  /| |     \033[0m ║
║  {colors[0]}  /__/     {colors[1]}\______/{colors[2]} /__/  \__\{colors[3]} /______/ {colors[4]}/__/ |_|     \033[0m ║

    """
    

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
    
    
    
    def home():
        pass
    
    intro()
    
    while True:
        key = read_key()
        if key == "ENTER":
            clear_shell()
            print("enter")
    
    