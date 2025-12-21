import os

import poker
import actionserver

def main():
    os.system("clear")
    
    game = poker.Game()
    print(game.community_cards)
    
    actionserver.run(game)

if __name__ == "__main__":
    main()