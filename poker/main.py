#!/usr/bin/env python3

# Michjzuman's Terminal Poker

import time
import random
import json
import math

from card import Card
from canvas import Canvas

def main():
    canvas = Canvas(
        fps=60,
        hold_window=0.12,
        auto_clear=False
    )

    def update(canvas):

        if canvas.just_pressed("q"):
            return False
        
        cards = [
            Card("K", "H")
        ]
        
        for card in cards:
            card.draw(canvas)
        
        canvas.border()

        if canvas.just_pressed(" "):
            canvas.clear()

        return True

    canvas.run(update)

if __name__ == "__main__":
    main()