import poker
import actionserver

def main():
    game = poker.Game()
    game.shuffle()
    print(game.stack)
    
    actionserver.run()

if __name__ == "__main__":
    main()