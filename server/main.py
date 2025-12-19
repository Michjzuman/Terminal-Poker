import os
import random
import time
import json
import math

import rules

class Game:
    def __init__(self):
        self.stack = [
            [
                (rank, suit)
                for rank in rules.ALL_RANKS
            ]
            for suit in rules.ALL_SUITS
        ]
        
def main():
    game = Game()
    print(game.stack)

if __name__ == "__main__":
    main()