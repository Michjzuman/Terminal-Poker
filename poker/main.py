#!/usr/bin/env python3

# Michjzuman's Terminal Poker

import time
import random
import json
import math

import ascii
import client
from canvas import Canvas

def main():
    canvas = Canvas(
        fps=10,
        hold_window=0.12,
        auto_clear=True
    )
    
    login = {
        "name": "Michjzuman",
        "password": "abc",
        "table_id": 0
    }
    
    table = client.get("table")["data"]
    community_cards = []
    for i, card in enumerate(table["community_cards"]):
        (rank, suit) = card
        community_cards.append(ascii.Card(rank, suit, 10 + i * 20, 10))

    def update():
        table = client.get("table")
        if table["ok"]:
            for i, card in enumerate(community_cards):
                card.rank = table["data"]["community_cards"][i][0]
                card.suit = table["data"]["community_cards"][i][1]
        
        client.post("handshake", {
            "name": login["name"],
            "password": login["password"],
            "table_id": login["table_id"]
        })

    update_interval = 0.5
    last_update = 0.0

    def frame(canvas):
        nonlocal last_update

        if canvas.just_pressed("q"):
            return False

        now = time.time()
        if now - last_update >= update_interval:
            update()
            last_update = now
        
        for card in community_cards:
            card.draw(canvas)
        
        ascii.border(canvas)

        if canvas.just_pressed(" "):
            canvas.clear()

        return True

    canvas.run(frame)

if __name__ == "__main__":
    main()
