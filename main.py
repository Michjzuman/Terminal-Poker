#!/usr/bin/env python3

# © Michjzuman

from datetime import datetime, timedelta
from itertools import combinations
import os
import platform
import random
import time
import shutil
import math
import json
import getpass
import asyncio

RED = "\033[31m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
YELLOW = "\033[38;5;214m"
GRAY = "\033[90m"
GREEN = "\033[32m"
RESET = "\033[0m"

ALL_KINDS = "CHSD"
ALL_NUMS = "234567891JQKA"

PATH = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(PATH, "users.json")
TABLE_FILE = os.path.join(PATH, "table.json")
ACTIVE_FILE = os.path.join(PATH, "active.json")

user = {}

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def read_file(f):
    if os.stat(f).st_size == 0:
        return {}
    with open(f, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def write_file(f, con):
    with open(f, "w") as file:
        file.write(json.dumps(con, indent=4))

def terminal_width():
    return shutil.get_terminal_size(fallback=(80, 24)).columns

def intro():
    pos = [RED, BLUE, PURPLE, YELLOW]

    def getText(prob, colors):
        text = f"""+--------------------------------------------------------+
|                                                        |
|                                                        |
|  {RED}   __  __   {BLUE}      __      {YELLOW}     /\      {PURPLE}     /\     {RESET}   |
|  {RED}  |  \/  |  {BLUE}    _(  )_    {YELLOW}    /  \     {PURPLE}    /  \    {RESET}   |
|  {RED}   \    /   {BLUE}   (__  __)   {YELLOW}    \  /     {PURPLE}   (_  _)   {RESET}   |
|  {RED}     \/     {BLUE}      ||      {YELLOW}     \/      {PURPLE}     ||     {RESET}   |
|                                                        |
|                                                        |
|                                                        |
|                 {GRAY}Michjzuman's Terminal-{RESET}                 |
|  {colors[0]}      _____ {colors[1]}   ____   {colors[2]}  ___ ___ {colors[3]}   _______ {colors[4]} _____    {RESET} |
|  {colors[0]}     /  _  |{colors[1]} /  __  \ {colors[2]} /  //  / {colors[3]}  /  ____/{colors[4]} /  _  |   {RESET} |
|  {colors[0]}    /   __/ {colors[1]}/  / /  /{colors[2]} /     /  {colors[3]}  /  /__ {colors[4]}  /     /    {RESET} |
|  {colors[0]}   /  /    {colors[1]}/  /_/  /{colors[2]} /  /\  \ {colors[3]}  /  /___ {colors[4]} /  /| |     {RESET} |
|  {colors[0]}  /__/     {colors[1]}\______/{colors[2]} /__/  \__\{colors[3]} /______/ {colors[4]}/__/ |_|     {RESET} |
|                                                        |
|                                                        |
+--------------------------------------------------------+"""
        
        text = list(text)
        for i in range(len(text)):
            if text[i] == " " and random.randint(0, prob) == 0:
                text[i] = random.choice("*@+$%:=<>")
        
        return ''.join(text)

    colors = [
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos),
        random.choice(pos)
    ]

    for i in range(25):
        if i % 5 == 0:
            colors = [
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos),
                random.choice(pos)
            ]
        text = getText(round(i**3), colors)
        clear()
        print(text)
        time.sleep(0.1)

def draw_cards(c):
    w = math.floor(terminal_width() / 12)
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
                "H": RED,
                "C": PURPLE,
                "D": YELLOW,
                "S": BLUE,
                "B": GRAY
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
                    text[i] = text[i][0] + color + text[i][1:-1] + RESET + text[i][-1]

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

def find_hands(cards):
    def royal_flush():
        res = []
        for kind in ALL_KINDS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([ALL_NUMS.index(card[1]) for card in flush_cards], reverse=True)

            if set(flush_values) >= {8, 9, 10, 11, 12}:
                res.append({"have": True, "points": sum(flush_values)})
        return res 
    def flush():
        res = []
        checked_kinds = set()
        for kind in ALL_KINDS:
            if kind in checked_kinds:
                continue
            checked_kinds.add(kind)
            hand = {"have": False}
            count = 0
            points = []
            for card in cards:
                if card[0] == kind:
                    count += 1
                    points.append(ALL_NUMS.index(card[1]) + 2)
            if count >= 5:
                hand["have"] = True
                for i in range(count - 4):
                    hand["points"] = sum(sorted(points[i:i + 5], reverse=True))
                    res.append(hand)
        return res
    def ofAKind(n):
        res = []
        checked_values = set()
        for card in cards:
            if card[1] in checked_values:
                continue
            checked_values.add(card[1])
            hand = {"have": False}
            count = 0
            points = []
            for checkCard in cards:
                if checkCard[1] == card[1]:
                    count += 1
                    points.append(ALL_NUMS.index(card[1]) + 2)
                    if count >= n:
                        hand["have"] = True
            if hand["have"]:
                hand["points"] = sum(sorted(points, reverse=True)[:n])
                res.append(hand)
        return res
    def straight():
        res = []
        points = []
        sorted_cards = sorted(cards, key=lambda card: ALL_NUMS.index(card[1]))
        for i in range(len(sorted_cards) - 4):
            hand = {"have": False}
            for j in range(i, i + 5):
                points.append(ALL_NUMS.index(sorted_cards[j][1]) + 2)
            
            if sorted(points) == list(range(min(points), max(points) + 1)):
                hand["have"] = True
                hand["points"] = sum(sorted(points, reverse=True))
                res.append(hand)
        return res
    def straight_flush():
        res = []
        for kind in ALL_KINDS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([ALL_NUMS.index(card[1]) for card in flush_cards], reverse=True)

            for i in range(len(flush_values) - 4):
                hand = {"have": False}
                straight_values = flush_values[i:i + 5]

                if straight_values[0] - straight_values[-1] == 4:
                    hand["have"] = True
                    hand["points"] = sum(straight_values)
                    res.append(hand)
        return res
    def full_house():
        res = []
        three_of_a_kind = ofAKind(3)
        pair = ofAKind(2)

        for three in three_of_a_kind:
            for two in pair:
                if three["points"] // 3 != two["points"] // 2:
                    res.append({
                        "have": True,
                        "points": three["points"] + two["points"]
                    })
        return res
    def two_pair():
        res = []
        pairs = ofAKind(2)

        if len(pairs) >= 2:
            for i in range(len(pairs) - 1):
                for j in range(i + 1, len(pairs)):
                    res.append({
                        "have": True,
                        "points": pairs[i]["points"] + pairs[j]["points"]
                    })
        return res
    def high_card():
        res = []
        for card in cards:
            res.append({
                "have": True,
                "points": ALL_NUMS.index(card[1]) + 2
            })
        return res
    
    hands = [
        royal_flush(),
        straight_flush(),
        ofAKind(4),
        full_house(),
        flush(),
        straight(),
        ofAKind(3),
        two_pair(),
        ofAKind(2),
        high_card()
    ]
    names = [
        "Royal Flush", "Straight Flush", "Four Of A Kind",
        "Full House", "Flush", "Straight", "Three Of A Kind",
        "Two Pair", "Pair", "High Card"
    ]

    def sort_hands(hands):
        return sorted(hands, key=lambda x: (names.index(x['hand']), -x['points']))

    res = []
    for i, hand in enumerate(hands):
        for h in hand:
            if h["have"]:
                res.append({"hand": names[i], "points": h["points"]})

    return sort_hands(res)

def drawAll():
    for num in ALL_NUMS:
        t = []
        for kind in ALL_KINDS:
            t.append(kind + num)
        draw_cards(t)
    draw_cards(["B"])

def menu(title, items):
    colors = [PURPLE, RED, BLUE, YELLOW]
    option_lines = ""
    for item in items:
        option_lines += f"""
|   {colors[items.index(item) % 4]}{item['title']}: {item['key']}{RESET}{' ' * (21 - len(item['title']))}|"""
        option_lines += """
|                           |"""

    text = f"""+---------------------------+{'' if title == "" else f'''
|                           |
|   {title}:{' ' * (23 - len(title))}|
|                           |'''}
|                           |{option_lines}
+---------------------------+
"""
    
    print(text)

    finished = False
    while not finished:
        choice = input("-> ")
        for item in items:
            if choice.lower() == item["key"]:
                finished = True
                if "att" in item:
                    item["action"](item["att"])
                else:
                    item["action"]()
        if not finished:
            print(f"{RED}Invalid Choice '{choice}'{RESET}")

def login():
    global user
    finished = False
    while not finished:
        username = input("Username: ")
        password = getpass.getpass("Password: ")

        users = read_file(USERS_FILE)
        for u in users:
            if u["name"] == username and u["password"] == password:
                finished = True
                user = u

        if not finished:
            print("Wrong Username Or Password")

def show_stats():
    global user
    clear()
    users = read_file(USERS_FILE)
    lines = ""
    for u in users:
        lines += f"|   {YELLOW if u['name'] == user['name'] else ''}{u['name']}:{RESET} {GREEN}{u['money']}*{RESET}{' ' * (21 - len(u['name']) - len(str(u['money'])))}|\n"
        lines += f"|                           |\n"
    text = f"""+---------------------------+
|                           |
{lines}+---------------------------+
"""
    print(text)
    def give():
        def do(uname):
            print()
            finished = False
            while not finished:
                howmuch = int(input(f"How Much?\n-> {GREEN}"))
                print(RESET)
                if user["money"] >= howmuch:
                    finished = True
                else:
                    print("Not Enough Money")
                    print()
            for i in range(len(users)):
                if users[i]["name"] == uname:
                    users[i]["money"] += howmuch
                if users[i]["name"] == user["name"]:
                    users[i]["money"] -= howmuch
            write_file(USERS_FILE, users)
            show_stats()

        print()
        users_list = []
        letters = list("abcdefghijklmnopqrstuvwxyz") + list(range(1000))
        i = 0
        for u in users:
            if user["name"] != u["name"]:
                users_list.append({
                    "title": u["name"],
                    "key": str(letters[i]),
                    "action": do,
                    "att": u["name"]
                })
                i += 1
        menu(f"Give Money To", users_list)
    menu("", [
        {
            "title": f"Give Someone Money",
            "key": "g",
            "action": give
        },
        {
            "title": "Back To Menu",
            "key": "b",
            "action": clear
        }
    ])

def poker():
    def shake_hand():
        data = read_file(ACTIVE_FILE)
        table = read_file(TABLE_FILE)
        if not {} in [data, table]:
            players = list(p["name"] for p in table["players"])
            if not user["name"] in players:
                join()
            dif = (datetime.now() - datetime.strptime(data["last"], "%H:%M:%S.%f %d.%m.%Y")).total_seconds()
            if dif > 0.3:
                if data["from"] == user["name"]:
                    if dif > 3:
                        if data["to"] in players:
                            table["players"].remove(table["players"][players.index(data["to"])])
                            table["logs"].append(f"{data['to']} Left  The Table")
                            write_file(TABLE_FILE, table)
                        data["to"] = user["name"]
                        write_file(ACTIVE_FILE, data)

                    if len(table["players"]) > 1:
                        if not table["playing"]:
                            start = (datetime.strptime(table["start-time"], "%H:%M:%S.%f %d.%m.%Y") - datetime.now()).total_seconds()
                            if start <= 0:
                                table["playing"] = True
                                table["turn"] = table["players"][0]["name"]
                                write_file(TABLE_FILE, table)
                    else:
                        if table["playing"]:
                            table["playing"] = False
                            write_file(TABLE_FILE, table)

                if data["to"] == user["name"]:
                    players = list(p["name"] for p in table["players"])
                    data["last"] = datetime.now().strftime("%H:%M:%S.%f %d.%m.%Y")
                    data["from"] = user["name"]
                    data["to"] = players[(players.index(user["name"]) + 1) % len(players)]
                    write_file(ACTIVE_FILE, data)

    def new_round():
        def startDeck():
            res = []
            for kind in ALL_KINDS:
                for num in ALL_NUMS:
                    res.append(kind + num)
            random.shuffle(res)
            return res
        
        deck = startDeck()
        print(TABLE_FILE)
        write_file(TABLE_FILE, {
            "logs": [f"{user['name']} Joined The Table"],
            "public_cards": [],
            "pool": 0,
            "turn": user["name"],
            "bet": 0,
            "playing": False,
            "round": "Pre-Flop",
            "times-raised": 0,
            "start-time": "00:00:00.000000 00.00.0000",
            "players": [
                {
                    "name": user["name"],
                    "money": user["money"],
                    "cards": deck[:2],
                    "in": True,
                    "bet": 0,
                    "all-in": False
                }
            ],
            "deck": deck[2:]
        })
        write_file(ACTIVE_FILE, {
            "last": datetime.now().strftime("%H:%M:%S.%f %d.%m.%Y"),
            "from": user["name"],
            "to": user["name"]
        })
        return data

    def join():
        data = read_file(TABLE_FILE)
        if data != {}:
            if data["playing"]:
                print("Waiting For New Round To Start...")
                data["logs"].append(f"{user['name']} Will Join Next Round")
                write_file(TABLE_FILE, data)
                while data["playing"]:
                    data = read_file(TABLE_FILE)
                    time.sleep(0.1)
            print("Joining...")

            if not user["name"] in list(p["name"] for p in data["players"]):
                data["players"].append({
                    "name": user["name"],
                    "money": user["money"],
                    "cards": data["deck"][:2],
                    "in": True,
                    "bet": 0,
                    "all-in": False
                })
                data["start-time"] = (datetime.now() + timedelta(seconds=20)).strftime("%H:%M:%S.%f %d.%m.%Y")
                data["deck"] = data["deck"][2:]
                data["logs"].append(f"{user['name']} Joined The Table")
                write_file(TABLE_FILE, data)
        else:
            join()
    
    def draw():
        table = read_file(TABLE_FILE)
        if table != {}:
            players = list(p["name"] for p in table["players"])

            lines = ""
            for p in table["players"]:
                icon = f"{RED}>{RESET}" if table["turn"] == p["name"] and table['playing'] else ' '
                color = YELLOW if p['name'] == user['name'] else ''
                name = f"{color}{p['name']}:{RESET}"
                lines += f"| {icon} {name} {GREEN}{p['money']}*{RESET}{' ' * (21 - len(p['name']) - len(str(p['money'])))}|\n"
                lines += "|                           |\n"
            print(f"""+---------------------------+\n|                           |\n{lines}+---------------------------+\n""")

            if table["playing"]:
                print(f"Pool: {GREEN}{table['pool']}*{RESET}")
                print()

                print("Public Cards:")
                draw_cards(table["public_cards"] + (["B"] * (5 - len(table["public_cards"]))))

                print("Your Cards:")
                players = list(p["name"] for p in table["players"])
                draw_cards(table["players"][players.index(user["name"])]["cards"])

            for log in table["logs"][-5:-1]:
                print(f"{GRAY}- {log}{RESET}")
            print(f"- {table['logs'][-1]}")

            print()

            if len(table["players"]) > 1:
                if not table["playing"]:
                    dif = (datetime.strptime(table["start-time"], "%H:%M:%S.%f %d.%m.%Y") - datetime.now()).total_seconds()
                    print(f"The Round Starts In {max(0, round(dif))} Seconds")
            else:
                print(f"Waiting For Other Players...")

            if table["playing"]:
                print(f"Bet: {GREEN}{table['bet']}*{RESET}")
                print()

    def turn():
        table = read_file(TABLE_FILE)
        if table != {}:
            players = list(p["name"] for p in table["players"])
            if table["playing"]:
                if table["turn"] == user["name"]:
                    users = read_file(USERS_FILE)
                    if users != {}:

                        # Check c
                        # Call c

                        # Bet b
                        # Raise r
                        # Re-Raise r

                        # Fold f

                        # All-In a

                        options = []

                        if table["bet"] <= user["money"]:
                            options.append(
                                {
                                    "name": "Check"
                                        if table["bet"] == 0 else "Call",
                                    "when": "c"
                                }
                            )
                        if table["times-raised"] <= 2:
                            options.append(
                                {
                                    "name": "Bet" 
                                        if table["times-raised"] == 0 else ("Raise"
                                        if table["times-raised"] <= 1 else "Re-Raise"),
                                    "when": "number"
                                }
                            )
                        if table["bet"] > 0:
                            options.append(
                                {
                                    "name": "Fold",
                                    "when": "f"
                                }
                            )
                        options.append(
                            {
                                "name": "All-In",
                                "when": "a"
                            }
                        )

                        print(options)

                        if table["turn"] == user["name"]:
                            write_file(TABLE_FILE, table)
                            write_file(USERS_FILE, users)
                else:
                    print(f"Waiting For {table['turn']}...")

    data = read_file(TABLE_FILE)

    dif = (datetime.now() - datetime.strptime(read_file(ACTIVE_FILE)["last"], "%H:%M:%S.%f %d.%m.%Y")).total_seconds()
    if dif < 5:
        join()
    else:
        new_round()
    
    end = False

    async def handshakes():
        while not end:
            shake_hand()
            await asyncio.sleep(0.1)

    async def play():
        nonlocal end
        task = asyncio.create_task(handshakes())

        try:
            while not end:
                clear()
                draw()
                turn()
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            end = True
            await task

    asyncio.run(play())

def main():
    #login()

    if terminal_width() >= 58:
        intro()

    clear()
    while True:
        menu("Menu", [
            {
                "title": "Show Stats",
                "key": "s",
                "action": show_stats
            },
            {
                "title": "Join Poker Table",
                "key": "p",
                "action": poker
            }
        ])

if __name__ == "__main__":
    main()
    #login()
    #poker()