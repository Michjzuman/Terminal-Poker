import json
import urllib.request
import urllib.error
import time

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

if __name__ == "__main__":
    import os
    os.system("clear; clear")
    
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
    
    time.sleep(25)
    
    # --- PREFLOP --- ---
    
    # micha bets big blind
    
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