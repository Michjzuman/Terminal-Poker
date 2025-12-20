#!/usr/bin/env python3

# Michjzuman's Terminal Poker

import time
import random
import json
import math

import ascii
from canvas import Canvas

def main():
    canvas = Canvas(
        fps=10,
        hold_window=0.12,
        auto_clear=True
    )

    def update(canvas):

        if canvas.just_pressed("q"):
            return False
        
        cards = [
            ascii.Card("6", "H")
        ]
        
        ascii.draw_card_back(canvas, 15, 20)
        
        for card in cards:
            card.draw(canvas)
        
        ascii.border(canvas)

        if canvas.just_pressed(" "):
            canvas.clear()

        return True

    canvas.run(update)

if __name__ == "__main__":
    main()