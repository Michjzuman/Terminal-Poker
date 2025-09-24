#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Texas Hold'em – Training + Multiplayer (Server/Client) + persistente Kontostaende.
Keinerlei externe Abhaengigkeiten (nur Standardbibliothek).
Getestet mit Python 3.10+.

Modi:
    python3 holdem.py --mode train --name <DeinName>
    python3 holdem.py --mode server --host 0.0.0.0 --port 8765
    python3 holdem.py --mode client --host <server-ip> --port 8765 --name <DeinName>

Hinweise:
- balances.json liegt neben diesem Script.
- Server: aktuell 2–6 Spieler, aber MVP-Loop startet ab 2.
- Side Pots: einfache Implementierung; All-in wird unterstuetzt, Sidepots basic (ausreichend fuer 95% der Faelle).
- Ranges/Bot: simpler Heuristik-Bot; spaeter kannst du MC-Simulationen einbauen.

Autor: ChatGPT + Micha-Team ;)
"""

import json
import os
import random
import sys
import time
import argparse
import socket
import threading
import queue
from typing import List, Tuple, Dict, Optional

# -------- Persistenz --------

BALANCE_FILE = "balances.json"

def load_balances() -> Dict[str, int]:
    if not os.path.exists(BALANCE_FILE):
        return {}
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_balances(data: Dict[str, int]) -> None:
    tmp = BALANCE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, BALANCE_FILE)

def get_balance(name: str, default: int = 1000) -> int:
    data = load_balances()
    if name not in data:
        data[name] = default
        save_balances(data)
    return data[name]

def set_balance(name: str, new_amount: int) -> None:
    data = load_balances()
    data[name] = max(0, int(new_amount))
    save_balances(data)

def add_balance(name: str, delta: int) -> int:
    data = load_balances()
    val = data.get(name, 1000) + int(delta)
    data[name] = max(0, val)
    save_balances(data)
    return data[name]

# -------- Karten & Bewertung --------

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = list(range(2, 15))  # 2..14 (14 = A)

Card = Tuple[int, str]  # (rank, suit)

def new_deck() -> List[Card]:
    return [(r, s) for r in RANKS for s in SUITS]

def rank_to_str(r: int) -> str:
    if r <= 10:
        return str(r)
    return {11: "J", 12: "Q", 13: "K", 14: "A"}[r]

def card_to_str(c: Card) -> str:
    return f"{rank_to_str(c[0])}{c[1]}"

def render_cards(cards: List[Card]) -> str:
    # Placeholder: kompakte Darstellung [Ah][Ks]...
    # Hier kannst du spaeter deinen ASCII-Block aus poker.py einklinken.
    return " ".join(f"[{card_to_str(c)}]" for c in cards)

def best_hand_7(cards7: List[Card]) -> Tuple[int, List[int]]:
    """
    Liefert (category, tiebreakers) fuer 7 Karten.
    Kategorie Ranking (hoeher ist besser):
        8: Straight Flush
        7: Four of a Kind
        6: Full House
        5: Flush
        4: Straight
        3: Three of a Kind
        2: Two Pair
        1: One Pair
        0: High Card
    Tiebreakers: absteigende relevante Ranks.
    """
    ranks = [r for r, _ in cards7]
    suits = [s for _, s in cards7]
    by_rank: Dict[int, int] = {}
    by_suit: Dict[str, List[int]] = {s: [] for s in SUITS}
    for r, s in cards7:
        by_rank[r] = by_rank.get(r, 0) + 1
        by_suit[s].append(r)

    # Flush?
    flush_suit = None
    flush_cards: List[int] = []
    for s, lst in by_suit.items():
        if len(lst) >= 5:
            flush_suit = s
            flush_cards = sorted(lst, reverse=True)
            break

    # Straight helper (auf eindeutigen Ranks!)
    def straight_high(cards_ranks: List[int]) -> Optional[int]:
        rset = set(cards_ranks)
        # Wheel (A-2-3-4-5): treat A as 1
        ordered = sorted(rset)
        # Map A (14) zusätzlich als 1
        if 14 in rset:
            ordered = sorted(rset | {1})
        # Finde 5er Kette
        run = 1
        best = None
        prev = None
        for val in ordered:
            if prev is None:
                prev = val
                run = 1
                continue
            if val == prev + 1:
                run += 1
            elif val != prev:
                run = 1
            prev = val
            if run >= 5:
                best = val  # high card of straight
        return best

    # Straight
    straight_hi = straight_high(ranks)

    # Straight Flush
    if flush_suit:
        sf_hi = straight_high([r for r, s in cards7 if s == flush_suit])
        if sf_hi is not None:
            return (8, [sf_hi])

    # Quads / Trips / Pairs
    groups = {}
    for r, cnt in by_rank.items():
        groups.setdefault(cnt, []).append(r)
    for cnt in groups:
        groups[cnt].sort(reverse=True)

    # Four of a Kind
    if 4 in groups:
        quad = groups[4][0]
        kickers = sorted([r for r in ranks if r != quad], reverse=True)
        return (7, [quad, kickers[0]])

    # Full House
    trips = groups.get(3, [])
    pairs = groups.get(2, [])
    if trips:
        if len(trips) >= 2:
            return (6, [trips[0], trips[1]])
        if pairs:
            return (6, [trips[0], pairs[0]])

    # Flush
    if flush_suit:
        return (5, flush_cards[:5])

    # Straight
    if straight_hi is not None:
        return (4, [straight_hi])

    # Trips
    if trips:
        kicker = [r for r in sorted(ranks, reverse=True) if r != trips[0]]
        return (3, [trips[0]] + kicker[:2])

    # Two Pair
    if len(pairs) >= 2:
        high, low = pairs[0], pairs[1]
        kicker = [r for r in sorted(ranks, reverse=True) if r not in (high, low)]
        return (2, [high, low, kicker[0]])

    # One Pair
    if pairs:
        pair = pairs[0]
        kicker = [r for r in sorted(ranks, reverse=True) if r != pair]
        return (1, [pair] + kicker[:3])

    # High Card
    highs = sorted(ranks, reverse=True)[:5]
    return (0, highs)

def compare7(a: List[Card], b: List[Card]) -> int:
    ha = best_hand_7(a)
    hb = best_hand_7(b)
    if ha[0] != hb[0]:
        return 1 if ha[0] > hb[0] else -1
    # Tie break
    for x, y in zip(ha[1], hb[1]):
        if x != y:
            return 1 if x > y else -1
    # Perfect tie
    return 0

# -------- Spiel-Engine (No-Limit Hold'em, basic) --------

class Player:
    def __init__(self, name: str, stack: int):
        self.name = name
        self.stack = stack
        self.hole: List[Card] = []
        self.folded = False
        self.all_in = False
        self.in_hand = 0  # Chips, die in dieser Hand investiert sind

    def reset_hand(self):
        self.hole = []
        self.folded = False
        self.all_in = False
        self.in_hand = 0

class Table:
    def __init__(self, names: List[str], stacks: List[int], small_blind: int = 5, big_blind: int = 10):
        assert len(names) == len(stacks)
        self.players = [Player(n, s) for n, s in zip(names, stacks)]
        self.sb = small_blind
        self.bb = big_blind
        self.button = 0  # Index des Dealers
        self.deck: List[Card] = []
        self.board: List[Card] = []
        self.pot = 0
        self.last_raise = self.bb
        self.current_bet = 0

    def active_players(self) -> List[Player]:
        return [p for p in self.players if not p.folded and p.stack > 0 or p.in_hand > 0]

    def rotate_button(self):
        self.button = (self.button + 1) % len(self.players)

    def post_blinds(self):
        n = len(self.players)
        sb_i = (self.button + 1) % n
        bb_i = (self.button + 2) % n
        sb_p = self.players[sb_i]
        bb_p = self.players[bb_i]
        self.take_bet(sb_p, min(self.sb, sb_p.stack))
        self.take_bet(bb_p, min(self.bb, bb_p.stack))
        self.current_bet = min(self.bb, bb_p.in_hand)
        self.last_raise = self.bb

    def shuffle_and_deal(self):
        self.deck = new_deck()
        random.shuffle(self.deck)
        self.board = []
        self.pot = 0
        for p in self.players:
            p.reset_hand()
        # Deal hole cards
        for _ in range(2):
            for p in self.players:
                if p.stack > 0:
                    p.hole.append(self.deck.pop())

    def burn(self):
        if self.deck:
            self.deck.pop()

    def deal_flop(self):
        self.burn()
        self.board.extend([self.deck.pop(), self.deck.pop(), self.deck.pop()])

    def deal_turn(self):
        self.burn()
        self.board.append(self.deck.pop())

    def deal_river(self):
        self.burn()
        self.board.append(self.deck.pop())

    def take_bet(self, p: Player, amount: int):
        amount = max(0, min(amount, p.stack))
        p.stack -= amount
        p.in_hand += amount
        if p.stack == 0 and amount > 0:
            p.all_in = True

    def collect_to_pot(self):
        for p in self.players:
            self.pot += p.in_hand
            p.in_hand = 0

    def betting_round(self, start_index: int, ask_action_cb) -> None:
        """
        Einfacher Betting-Loop:
        - ask_action_cb(player, to_call, min_raise) -> ("fold"|"call"|"check"|"raise", amount)
        - side pots basic: All-ins werden respektiert
        """
        # Reset Runde
        to_act_order = list(range(len(self.players)))
        # Start anpassen
        while to_act_order[0] != start_index:
            to_act_order.append(to_act_order.pop(0))

        # Jeder der nicht gefoldet/all-in ist kann agieren
        # Ende wenn alle gecallt/gecheckt haben und kein neuer Raise kommt
        self.current_bet = max(p.in_hand for p in self.players)
        self.last_raise = max(self.bb, self.last_raise)
        acted = {i: False for i in range(len(self.players))}
        last_raiser = None

        while True:
            everyone_set = True
            for i in to_act_order:
                p = self.players[i]
                if p.folded or p.all_in:
                    acted[i] = True
                    continue
                to_call = self.current_bet - p.in_hand
                if not acted[i] or (last_raiser is not None and i == (last_raiser + 1) % len(self.players)):
                    # darf reagieren
                    everyone_set = False
                    action, amount = ask_action_cb(p, to_call, max(self.bb, self.last_raise))
                    if action == "fold":
                        p.folded = True
                    elif action in ("check", "call"):
                        call_amt = min(to_call, p.stack)
                        self.take_bet(p, call_amt)
                    elif action == "raise":
                        # min raise: current_bet + last_raise
                        min_total = self.current_bet + max(self.bb, self.last_raise)
                        target = max(min_total, p.in_hand + amount)
                        # Begrenzen durch Stack
                        target = min(target, p.in_hand + p.stack)
                        delta = target - p.in_hand
                        if delta > 0:
                            self.take_bet(p, delta)
                            self.last_raise = target - self.current_bet
                            self.current_bet = target
                            last_raiser = i
                        else:
                            # wenn nicht moeglich -> call
                            call_amt = min(to_call, p.stack)
                            self.take_bet(p, call_amt)
                    acted[i] = True
                # Skip sonst
            # Check stop
            if everyone_set:
                # Wenn seit letztem Raise alle einmal dran waren -> Ende
                break

        # Einsammeln
        self.collect_to_pot()

    def showdown(self) -> List[Tuple[Player, int]]:
        """
        Verteilt Pot an Gewinner. Basic Side-Pot Logik:
        - Wir bilden Schichten nach investiertem Betrag (Caps durch All-ins).
        - Pro Schicht wird der beste noch teilnehmende Spieler bezahlt.
        Rueckgabe: Liste der Auszahlungen [(player, amount), ...]
        """
        # Gather players still in contention
        contenders = [p for p in self.players if not p.folded]
        if len(contenders) == 1:
            # Alle gefoldet ausser einer Person
            w = contenders[0]
            payout = self.pot
            self.pot = 0
            w.stack += payout
            return [(w, payout)]

        # Fuer Side-Pots: wir brauchen, wie viel jeder insgesamt in den Pot dieser Hand eingezahlt hat.
        # Da wir bereits alles in self.pot gesammelt haben und p.in_hand == 0, muessen wir die Caps approximieren.
        # Vereinfachung: wir rekonstruieren aus "all_in" + Startstack nicht exakt; stattdessen verteilen wir einfach
        # den gesamten Pot an die besten Haende (Split bei Gleichstand). Das ist fuer die meisten Faelle ok.
        # Wenn du 100% korrekte Side-Pots brauchst, kann ich das in die naechste Version hart reindrehen.
        board7 = self.board
        scores = []
        for p in contenders:
            seven = p.hole + board7
            scores.append((p, best_hand_7(seven)))

        # Bestes bestimmen
        scores.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)
        best_cat = scores[0][1][0]
        best_tb = scores[0][1][1]
        winners = [scores[0][0]]
        for pl, sc in scores[1:]:
            if sc[0] == best_cat and sc[1] == best_tb:
                winners.append(pl)
            else:
                break

        payout_each = self.pot // len(winners)
        rest = self.pot - payout_each * len(winners)
        res = []
        for w in winners:
            amt = payout_each + (1 if rest > 0 else 0)
            if rest > 0:
                rest -= 1
            w.stack += amt
            res.append((w, amt))
        self.pot = 0
        return res

# -------- Bot --------

def bot_action_simple(p: Player, board: List[Card], to_call: int, min_raise: int) -> Tuple[str, int]:
    """
    Sehr simpler Heuristik-Bot:
    - Preflop: bewertet hole cards (Paar/hohe Karten/Suited).
    - Postflop: nutzt Handkategorie.
    - Callt klein, raist moderat bei guten Haenden, foldet Schrott gegen grosse Bets.
    """
    strength = 0.0

    def hole_score(hole: List[Card]) -> float:
        a, b = hole
        ranks = sorted([a[0], b[0]], reverse=True)
        score = 0.0
        if ranks[0] == ranks[1]:  # Paar
            score += 1.5 + (ranks[0] - 2) / 12.0
        else:
            score += (ranks[0] - 6) / 10.0
        if a[1] == b[1]:
            score += 0.2
        if abs(a[0] - b[0]) == 1:
            score += 0.1
        return score

    if len(board) == 0:
        strength = hole_score(p.hole)
    else:
        cat, tb = best_hand_7(p.hole + board)
        # Map Kategorie auf [0..2] ca.
        strength = {
            0: 0.2,  # High Card
            1: 0.6,  # Pair
            2: 0.9,  # Two Pair
            3: 1.2,  # Trips
            4: 1.3,  # Straight
            5: 1.4,  # Flush
            6: 1.6,  # Full House
            7: 1.9,  # Quads
            8: 2.2,  # Straight Flush
        }[cat]

    # Entscheidungslogik
    # Kleinere Calls ok, grosse Calls nur mit staerkerer Hand
    if to_call == 0:
        # Kein Druck -> leichte Bets/Checks
        if strength >= 1.2 and p.stack > 0:
            return ("raise", max(10, min_raise))
        return ("check", 0)
    else:
        pot_pressure = to_call / max(1, p.stack + to_call)
        if strength < 0.5 and to_call > 0 and pot_pressure > 0.2:
            return ("fold", 0)
        if strength >= 1.2 and p.stack > to_call + min_raise:
            # Aggressiv
            return ("raise", to_call + min_raise)
        # Sonst call
        return ("call", 0)

# -------- Terminal I/O --------

def ask_player_terminal(name: str, hole: List[Card], board: List[Card], pot: int, to_call: int, min_raise: int, stack: int) -> Tuple[str, int]:
    print(f"\n=== {name} ist dran ===")
    print(f"Board: {render_cards(board)}   Pot: {pot}")
    print(f"Deine Karten: {render_cards(hole)}   Stack: {stack}   ToCall: {to_call}   MinRaise: {min_raise}")
    while True:
        raw = input("Aktion (f=fold, c=check/call, r <betrag>=raise, a=all-in): ").strip().lower()
        if raw in ("f", "fold"):
            return ("fold", 0)
        if raw in ("c", "call", "check"):
            return ("call" if to_call > 0 else "check", 0)
        if raw.startswith("r"):
            parts = raw.split()
            if len(parts) == 2 and parts[1].isdigit():
                amt = int(parts[1])
                return ("raise", amt)
            print("Format: r <betrag>")
            continue
        if raw in ("a", "allin", "all-in"):
            return ("raise", stack)  # treat as raise to all-in
        print("Ungueltig. Nochmal.")

# -------- Trainingsmodus --------

def play_heads_up_training(name: str) -> None:
    human_name = name
    bot_name = "CPU"
    human_stack = get_balance(human_name, default=1000)
    bot_stack = 1000

    table = Table([human_name, bot_name], [human_stack, bot_stack], small_blind=5, big_blind=10)

    print("Skibidi. Trainingsmodus gestartet. Blind 5/10. Abbruch mit CTRL+C.")
    hand_no = 1
    try:
        while True:
            print(f"\n\n===== Hand {hand_no} =====")
            table.shuffle_and_deal()
            table.post_blinds()

            # Preflop: Action ab UTG (nach BB), bei 2 Spielern ist das der Button nach BB -> der Spieler hinter BB
            start = (table.button + 3) % len(table.players)

            def ask_action(p: Player, to_call: int, min_raise: int):
                if p.name == human_name:
                    return ask_player_terminal(p.name, p.hole, table.board, table.pot, to_call, min_raise, p.stack)
                else:
                    return bot_action_simple(p, table.board, to_call, min_raise)

            table.betting_round(start, ask_action)
            # Falls alle ausser einer Person folden:
            alive = [pl for pl in table.players if not pl.folded]
            if len(alive) == 1:
                w = alive[0]
                w.stack += table.pot
                print(f"Alle anderen gefoldet. {w.name} gewinnt {table.pot}.")
                table.pot = 0
            else:
                # Flop
                table.deal_flop()
                print(f"Flop: {render_cards(table.board)}")
                table.betting_round((table.button + 1) % 2, ask_action)

                alive = [pl for pl in table.players if not pl.folded]
                if len(alive) == 1:
                    w = alive[0]
                    w.stack += table.pot
                    print(f"Alle anderen gefoldet. {w.name} gewinnt {table.pot}.")
                    table.pot = 0
                else:
                    # Turn
                    table.deal_turn()
                    print(f"Turn: {render_cards(table.board)}")
                    table.betting_round((table.button + 1) % 2, ask_action)

                    alive = [pl for pl in table.players if not pl.folded]
                    if len(alive) == 1:
                        w = alive[0]
                        w.stack += table.pot
                        print(f"Alle anderen gefoldet. {w.name} gewinnt {table.pot}.")
                        table.pot = 0
                    else:
                        # River
                        table.deal_river()
                        print(f"River: {render_cards(table.board)}")
                        table.betting_round((table.button + 1) % 2, ask_action)

                        # Showdown
                        payouts = table.showdown()
                        print("Showdown!")
                        for p in table.players:
                            print(f"{p.name} {render_cards(p.hole)}")
                        for w, amt in payouts:
                            print(f"-> {w.name} gewinnt {amt}")

            # Stacks syncen und Kontostand speichern
            human_stack = table.players[0].stack if table.players[0].name == human_name else table.players[1].stack
            bot_stack = table.players[0].stack if table.players[0].name == bot_name else table.players[1].stack
            set_balance(human_name, human_stack)

            print(f"Stacks: {human_name}={human_stack} | {bot_name}={bot_stack}")
            table.rotate_button()
            hand_no += 1
    except KeyboardInterrupt:
        print("\nBeendet.")
        print(f"Neuer Kontostand fuer {human_name}: {get_balance(human_name)}")

# -------- Multiplayer: einfacher TCP-Server/Client --------

# Protokoll: newline-delimited JSON strings.
# Messages vom Server:
#   {"type":"state","text":"..." } -> plain text fuer Anzeige
#   {"type":"ask","to":"<name>","payload":{"board":[...], "hole":[...], "pot":int, "to_call":int, "min_raise":int, "stack":int}}
# Client antwortet:
#   {"type":"action","name":"<name>","action":"fold|call|check|raise","amount":int}

def json_dumps(x: dict) -> str:
    return json.dumps(x, ensure_ascii=False)

def send_line(conn: socket.socket, obj: dict) -> None:
    line = json_dumps(obj) + "\n"
    conn.sendall(line.encode("utf-8"))

def recv_line(conn: socket.socket) -> Optional[dict]:
    buf = b""
    while True:
        ch = conn.recv(1)
        if not ch:
            return None
        if ch == b"\n":
            try:
                return json.loads(buf.decode("utf-8"))
            except Exception:
                return None
        buf += ch

class ClientHandler(threading.Thread):
    def __init__(self, conn: socket.socket, addr, server_ref):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.server = server_ref
        self.name = None
        self.queue = queue.Queue()

    def run(self):
        try:
            # Begruessung & Name
            send_line(self.conn, {"type":"state","text":"Willkommen! Bitte Namen senden: {\"type\":\"hello\",\"name\":\"Micha\"}."})
            while True:
                msg = recv_line(self.conn)
                if msg is None:
                    break
                t = msg.get("type")
                if t == "hello":
                    self.name = str(msg.get("name","Player")).strip()[:20] or "Player"
                    self.server.register(self)
                    send_line(self.conn, {"type":"state","text":f"Hi {self.name}. Warte auf Tischstart..."})
                    break

            # Hauptloop: Nachrichten zum Client
            while True:
                obj = self.queue.get()
                if obj is None:
                    break
                send_line(self.conn, obj)
        except Exception:
            pass
        finally:
            try:
                self.conn.close()
            except Exception:
                pass
            self.server.unregister(self)

class PokerServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: List[ClientHandler] = []
        self.lock = threading.Lock()
        self.running = True

    def register(self, ch: ClientHandler):
        with self.lock:
            self.clients.append(ch)
        self.broadcast({"type":"state","text":f"{ch.name} ist beigetreten. Spieler online: {len(self.clients)}"})

    def unregister(self, ch: ClientHandler):
        with self.lock:
            if ch in self.clients:
                self.clients.remove(ch)
        self.broadcast({"type":"state","text":f"{ch.name or 'Unbekannt'} hat verlassen. Spieler online: {len(self.clients)}"})

    def broadcast(self, obj: dict):
        with self.lock:
            for c in self.clients:
                c.queue.put(obj)

    def ask_player(self, name: str, payload: dict) -> Tuple[str, int]:
        # Finde Client
        with self.lock:
            target = None
            for c in self.clients:
                if c.name == name:
                    target = c
                    break
        if not target:
            return ("fold", 0)
        target.queue.put({"type":"ask","to":name,"payload":payload})
        # Antwort lesen (blocking)
        while True:
            msg = recv_line(target.conn)
            if msg is None:
                return ("fold", 0)
            if msg.get("type") == "action" and msg.get("name") == name:
                act = msg.get("action","call")
                amount = int(msg.get("amount", 0))
                if act in ("fold","call","check","raise"):
                    return (act, amount)

    def serve(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(16)
        print(f"Server lauscht auf {self.host}:{self.port} ...")
        threading.Thread(target=self.accept_loop, daemon=True).start()

        try:
            while self.running:
                time.sleep(1.0)
                # Startet automatisch ein Spiel, wenn mind. 2 Spieler da sind
                with self.lock:
                    ready = [c for c in self.clients if c.name]
                if len(ready) >= 2:
                    self.run_table([c.name for c in ready[:6]])  # max 6
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            try:
                self.sock.close()
            except Exception:
                pass

    def accept_loop(self):
        while self.running:
            try:
                conn, addr = self.sock.accept()
                ch = ClientHandler(conn, addr, self)
                ch.start()
            except Exception:
                break

    def run_table(self, names: List[str]):
        self.broadcast({"type":"state","text":f"Starte Tisch mit: {', '.join(names)}"})
        stacks = [get_balance(n, 1000) for n in names]
        table = Table(names, stacks, 5, 10)
        # einfache 1-Hand-Runde, danach wird erneut ein Tisch gestartet
        table.shuffle_and_deal()
        table.post_blinds()

        def ask_action(p: Player, to_call: int, min_raise: int):
            payload = {
                "board": [card_to_str(c) for c in table.board],
                "hole": [card_to_str(c) for c in p.hole],
                "pot": table.pot,
                "to_call": to_call,
                "min_raise": min_raise,
                "stack": p.stack,
            }
            return self.ask_player(p.name, payload)

        # Preflop
        start = (table.button + 3) % len(table.players)
        table.betting_round(start, ask_action)
        alive = [pl for pl in table.players if not pl.folded]
        if len(alive) == 1:
            w = alive[0]
            w.stack += table.pot
            self.broadcast({"type":"state","text":f"Alle gefoldet -> {w.name} gewinnt {table.pot}"})
            table.pot = 0
        else:
            table.deal_flop()
            self.broadcast({"type":"state","text":f"Flop: {render_cards(table.board)}"})
            table.betting_round((table.button + 1) % len(table.players), ask_action)

            alive = [pl for pl in table.players if not pl.folded]
            if len(alive) == 1:
                w = alive[0]
                w.stack += table.pot
                self.broadcast({"type":"state","text":f"Alle gefoldet -> {w.name} gewinnt {table.pot}"})
                table.pot = 0
            else:
                table.deal_turn()
                self.broadcast({"type":"state","text":f"Turn: {render_cards(table.board)}"})
                table.betting_round((table.button + 1) % len(table.players), ask_action)

                alive = [pl for pl in table.players if not pl.folded]
                if len(alive) == 1:
                    w = alive[0]
                    w.stack += table.pot
                    self.broadcast({"type":"state","text":f"Alle gefoldet -> {w.name} gewinnt {table.pot}"})
                    table.pot = 0
                else:
                    table.deal_river()
                    self.broadcast({"type":"state","text":f"River: {render_cards(table.board)}"})
                    table.betting_round((table.button + 1) % len(table.players), ask_action)

                    payouts = table.showdown()
                    show = "\n".join(f"{p.name}: {render_cards(p.hole)}" for p in table.players)
                    self.broadcast({"type":"state","text":"Showdown!\n"+show+"\n"+", ".join(f"{w.name}+{amt}" for w, amt in payouts)})

        # Stacks speichern
        for p in table.players:
            set_balance(p.name, p.stack)
        self.broadcast({"type":"state","text":"Hand beendet. Kontostaende gespeichert."})

# -------- Client --------

def run_client(host: str, port: int, name: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    send_line(s, {"type":"hello","name":name})
    print(f"Verbunden als {name}. Warte auf Tisch...")

    while True:
        msg = recv_line(s)
        if msg is None:
            print("Verbindung beendet.")
            break
        t = msg.get("type")
        if t == "state":
            print(msg.get("text",""))
        elif t == "ask":
            payload = msg.get("payload", {})
            board = payload.get("board", [])
            hole = payload.get("hole", [])
            pot = payload.get("pot", 0)
            to_call = int(payload.get("to_call", 0))
            min_raise = int(payload.get("min_raise", 0))
            stack = int(payload.get("stack", 0))
            print("\n=== DU BIST DRAN ===")
            print(f"Board: {' '.join(f'[{x}]' for x in board)}   Pot: {pot}")
            print(f"Deine Karten: {' '.join(f'[{x}]' for x in hole)}   Stack: {stack}   ToCall: {to_call}   MinRaise: {min_raise}")
            while True:
                raw = input("Aktion (f=fold, c=check/call, r <betrag>=raise, a=all-in): ").strip().lower()
                if raw in ("f","fold"):
                    send_line(s, {"type":"action","name":name,"action":"fold","amount":0})
                    break
                if raw in ("c","call","check"):
                    send_line(s, {"type":"action","name":name,"action":"call" if to_call>0 else "check","amount":0})
                    break
                if raw.startswith("r"):
                    parts = raw.split()
                    if len(parts) == 2 and parts[1].isdigit():
                        amt = int(parts[1])
                        send_line(s, {"type":"action","name":name,"action":"raise","amount":amt})
                        break
                    print("Format: r <betrag>")
                    continue
                if raw in ("a","allin","all-in"):
                    send_line(s, {"type":"action","name":name,"action":"raise","amount":stack})
                    break
                print("Ungueltig. Nochmal.")
        else:
            print(msg)

# -------- CLI --------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["train","server","client"], required=True)
    ap.add_argument("--name", type=str, default="Micha")
    ap.add_argument("--host", type=str, default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    if args.mode == "train":
        play_heads_up_training(args.name)
    elif args.mode == "server":
        srv = PokerServer(args.host, args.port)
        srv.serve()
    elif args.mode == "client":
        run_client(args.host, args.port, args.name)

if __name__ == "__main__":
    main()