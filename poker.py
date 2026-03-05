from enum import Enum
from dataclasses import dataclass
import random

class Rank(Enum):
    TWO = "2"  
    THREE = "3"  
    FOUR = "4"  
    FIVE = "5"  
    SIX = "6"  
    SEVEN = "7"  
    EIGHT = "8"  
    NINE = "9"  
    TEN = "10"  
    JACK = "J"  
    QUEEN = "Q"  
    KING = "K"  
    ACE = "A"  

    @property
    def number(self) -> int:
        return {
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14
        }[self]

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

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank: Rank = rank
        self.suit: Suit = suit
    
    def ascii(self, old_design: bool = False):
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
                return self.suit.symbol if not self.rank in l else ' '
            def b(l: list[str]):
                return self.suit.symbol if self.rank in l else ' '
            design = [
                f"┌───────┐",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"│   {b(['7', '8', '9', '10'])}   │",
                f"│ {b(['6', '7', '8', '9', '10'])} {b(['A', '3', '5'])} {b(['6', '7', '8', '9', '10'])} │",
                f"│ {b(['9', '10'])} {b(['8', '10'])} {b(['9', '10'])} │",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"└───────┘",
                f" {' ' if len(str(self.rank)) == 1 else ''} {self.rank} {self.suit.symbol}   "
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
            result.append(f"{line[0]}{self.suit.color}{line[1:-1]}\033[0m{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{self.suit.color}{design[-1]}\033[0m")
        
        return result

class HandRank(Enum):
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

@dataclass
class Hand:
    rank: HandRank
    cards: list[Card]

class Phase(Enum):
    PREFLOP = "Preflop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"
    
    @property
    def amount_of_cards(self):
        return {
            Phase.PREFLOP: 0,
            Phase.FLOP: 3,
            Phase.TURN: 1,
            Phase.RIVER: 1
        }[self]
    
    @property
    def next(self):
        return {
            Phase.PREFLOP: Phase.FLOP,
            Phase.FLOP: Phase.TURN,
            Phase.TURN: Phase.RIVER,
            Phase.RIVER: None,
        }[self]

class MoveType(Enum):
    CHECK = "Check"
    CALL = "Call"
    
    BET = "Bet"
    RAISE = "Raise"
    
    FOLD = "Fold"

@dataclass
class Move:
    type: MoveType
    amount: int = None

class Player:
    def __init__(self, name: str, money: int):
        self.name: str = name
        self.money: int = money
        self.cards: list[Card] = []
        self.bet: int = 0
        self.is_in: bool = True
        self.game: "Game"
    
    def do_move(self, move: Move):
        if move.type in [MoveType.CHECK, MoveType.CALL]:
            self.money -= self.game.bet - self.bet
            self.bet = self.game.bet
        
        if move.type in [MoveType.BET, MoveType.RAISE]:
            self.money -= move.amount
            self.bet += move.amount
            self.game.bet += move.amount
        
        elif move.type in [MoveType.FOLD]:
            self.is_in = False

class Game:
    def __init__(self, *players: Player, pool: int = 0, small_blind: int = 1, big_blind: int = 2):
        self.stack: list[Card] = [
            Card(rank, suit)
            for rank in list(Rank)
            for suit in list(Suit)
        ]
        
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind
        
        self.community_cards: list[Card] = []
        
        self.finished: bool = False
        self.turn: int = 2
        
        self.players: list[Player] = list(players)
        for player in self.players:
            player.game = self
        
        self.phase: Phase = Phase.PREFLOP
        self.bet: int = 0
        self.pool: int = pool
    
    def deal_cards(self):
        random.shuffle(self.stack)
        for player in self.players:
            player.cards += self.stack[-2:]
            self.stack = self.stack[:-2]
    
    def next_phase(self):
        if self.phase.next == None:
            self.finished = True
        else:
            self.phase = self.phase.next
            self.community_cards += self.stack[-self.phase.amount_of_cards:]
            self.stack = self.stack[:-self.phase.amount_of_cards]
            
            for player in self.players:
                self.pool += player.bet
                player.bet = 0

    def play_round(self):
        
        return


if __name__ == "__main__":
    import os
    import time
    import play
    
    game = Game(
        Player("Hans", 67),
        Player("Fritz", 41)
    )
    
    game.deal_cards()
    
    while not game.finished:
        os.system("clear; clear")
        
        print(f"\033[32m{game.pool}*\033[0m")
        play.print_cards_in_line(*game.community_cards)
        
        print()
        
        print(f"{game.players[0].name} \033[32m{game.players[0].money}*\033[0m")
        play.print_cards_in_line(*game.players[0].cards)
        
        print()
        
        print(f"{game.players[1].name} \033[32m{game.players[1].money}*\033[0m")
        play.print_cards_in_line(*game.players[1].cards)
        
        game.players[0].do_move(Move(MoveType.BET, 10))
        
        game.next_phase()
        
        time.sleep(1)
