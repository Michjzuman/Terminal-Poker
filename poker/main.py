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
        fps=60,
        hold_window=0.12,
        auto_clear=False
    )

    def update(canvas):

        if canvas.just_pressed("q"):
            return False
        
        canvas.draw(10, 5, ascii.card("K", "H", True))
        canvas.draw(10, 30, ascii.card("Q", "D"))
        canvas.draw(70, 30, ascii.card("J", "S"))
        canvas.draw(50, 10, ascii.card("10", "C", True))
        
        ascii.border(canvas)

        if canvas.just_pressed(" "):
            canvas.clear()

        return True

    canvas.run(update)

if __name__ == "__main__":
    main()