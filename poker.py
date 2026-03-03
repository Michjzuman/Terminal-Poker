from enum import IntEnum, Enum

class Settings:
    def __init__(self):
        self.old_design = False

settings = Settings()

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
    
    @property
    def ascii(self):
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
        
        if settings.old_design:
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
            result.append(f"{line[0]}{self.suit.color}{line[1:-1]}\033[0m{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{self.suit.color}{design[-1]}\033[0m")
        
        return result

class Hand_Rank(Enum):
    ROYAL_FLUSH = 1
    STRAIGHT_FLUSH = 2
    FOUR_OF_A_KIND = 3
    FULL_HOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    THREE_OF_A_KIND = 7
    TWO_PAIR = 8
    PAIR = 9
    HIGH_CARD = 10

class Hand:
    def __init__(self, rank: Hand_Rank, *cards: Card):
        self.rank: Hand_Rank = rank
        self.cards: list[Card] = cards

def find_hands(*cards: Card) -> list[Hand]:
    def high_card() -> list[Hand]:
        return
    return



class Player:
    def __init__(self, name: str, money: int):
        self.name: str = name
        self.money: int = money
        self.cards: list[Card] = []

class Phase(Enum):
    PREFLOP = "Preflop"
    FLOP = "Flop"
    RIVER = "River"
    TURN = "Turn"
    
    @property
    def amount_of_cards(self):
        return {
            Phase.PREFLOP: 0,
            Phase.FLOP: 3,
            Phase.RIVER: 1,
            Phase.TURN: 1,
        }[self]
    
    @property
    def next(self):
        return {
            Phase.PREFLOP: Phase.FLOP,
            Phase.FLOP: Phase.RIVER,
            Phase.RIVER: Phase.TURN,
            Phase.TURN: None,
        }[self]

class Game:
    def __init__(self, *players: Player, pool: int = 0):
        self.phase: Phase = Phase.PREFLOP
        self.pool: int = pool
        self.players: list[Player] = list(players)
        self.community_cards: list[Card] = []
        self.stack: list[Card] = [
            Card(rank, suit)
            for rank in list(Rank)
            for suit in list(Suit)
        ]

    def next_phase(self):
        self.phase = self.phase.next

if __name__ == "__main__":
    import os
    os.system("clear; clear")
    
    card = Card(Rank.SEVEN, Suit.HEARTS)
    print("\n".join(card.ascii))
    
    game = Game(
        Player("Hans", 67),
        Player("Fritz", 41),
        pool = 5
    )