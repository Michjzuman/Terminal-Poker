from enum import IntEnum, Enum
import os

class Suit(Enum):
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"

    @property
    def short(self) -> str:
        return self.value

    @property
    def symbol(self) -> str:
        return {
            Suit.CLUBS: "♣",
            Suit.DIAMONDS: "♦",
            Suit.HEARTS: "♥",
            Suit.SPADES: "♠",
        }[self]
    
    @property
    def color(self) -> str:
        return {
            Suit.CLUBS: "\033[33m",
            Suit.DIAMONDS: "\033[35m",
            Suit.HEARTS: "\033[31m",
            Suit.SPADES: "\033[34m",
        }[self]

    def __str__(self) -> str:
        return self.symbol

class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def letter(self) -> str:
        return {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A",
        }[self]

    def __str__(self) -> str:
        return self.letter

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def ascii(self, old_design = True):
        if self.rank == Rank.KING:
            design = [
                f"┌───────┐",
                f"│  www  │",
                f"│  [{self.suit.symbol}]  │",
                f"│ _/_\\_ │",
                f"││+ † +││",
                f"│ - - - │",
                f"└───────┘",
                f"   K {self.suit.symbol}   "
            ]
        elif self.rank == Rank.QUEEN:
            design = [
                f"┌───────┐",
                f"│  www  │",
                f"│  ({self.suit.symbol})  │",
                f"│ _)*(_ │",
                f"│(~~V~~)│",
                f"│ - - - │",
                f"└───────┘",
                f"   Q {self.suit.symbol}   "
            ]
        elif self.rank == Rank.JACK:
            design = [
                f"┌───────┐",
                f"│  ,=~  │",
                f"│  [{self.suit.symbol}{'}'}  │",
                f"│ _/_\\_ │",
                f"│|\\ |:/|│",
                f"│ - - - │",
                f"└───────┘",
                f"   J {self.suit.symbol}   "
            ]
        else:
            def a(l: list[str]):
                return self.suit.symbol if not self.rank.letter in l else ' '
            def b(l: list[str]):
                return self.suit.symbol if self.rank.letter in l else ' '
            design = [
                f"┌───────┐",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"│   {b(['7', '8', '9', '10'])}   │",
                f"│ {b(['6', '7', '8', '9', '10'])} {b(['A', '3', '5'])} {b(['6', '7', '8', '9', '10'])} │",
                f"│ {b(['9', '10'])} {b(['8', '10'])} {b(['9', '10'])} │",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"└───────┘",
                f" {' ' if len(self.rank.letter) == 1 else ''} {self.rank} {self.suit.symbol}   "
            ]
        
        if old_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌───────┐", "+-------+")
                    .replace("│", "|")
                    .replace("└───────┘", "+-------+")
                )
            design = updated_design
        
        result = design[:1]
        
        for line in design[1:-2]:
            result.append(f"{line[0]}{self.suit.color}{line[1:-1]}{"\033[0m"}{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{self.suit.color}{design[-1]}{"\033[0m"}")
        
        return result

if __name__ == "__main__":
    os.system("clear; clear")
    for rank in list(Rank):
        card = Card(rank, Suit.HEARTS)
        print("\n".join(card.ascii()))