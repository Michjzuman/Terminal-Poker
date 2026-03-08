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
    
    def ascii(self, *,
            old_design: bool = False,
            round_design: bool = False,
            thick_design: bool = False,
            royal_design: bool = False,
            dashed_design: bool = False,
            fancy_design: bool = False
        ):
        
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
        elif self.rank == Rank.ACE and self.suit == Suit.SPADES:
            design = [
                f"┌───────┐",
                f"│       │",
                f"│  /A\  │",
                f"│ (@♠@) │",
                f"│  /_\  │",
                f"│       │",
                f"└───────┘",
                f"   A ♠   "
            ]
        else:
            def a(l: list[str]):
                return self.suit.symbol if not self.rank.value in l else ' '
            def b(l: list[str]):
                return self.suit.symbol if self.rank.value in l else ' '
            design = [
                f"┌───────┐",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"│   {b(['7', '8', '9', '10'])}   │",
                f"│ {b(['6', '7', '8', '9', '10'])} {b(['A', '3', '5'])} {b(['6', '7', '8', '9', '10'])} │",
                f"│ {b(['9', '10'])} {b(['8', '10'])} {b(['9', '10'])} │",
                f"│ {a(['A', '2', '3'])} {b(['2', '3'])} {a(['A', '2', '3'])} │",
                f"└───────┘",
                f" {' ' if len(self.rank.value) == 1 else ''} {self.rank.value} {self.suit.symbol}   "
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
        elif round_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌", "╭")
                    .replace("└", "╰")
                    .replace("┐", "╮")
                    .replace("┘", "╯")
                )
            design = updated_design
        elif thick_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌───────┐", "╔═══════╗")
                    .replace("│", "║")
                    .replace("└───────┘", "╚═══════╝")
                )
            design = updated_design
        elif royal_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌───────┐", "╔┄┄┄┄┄┄┄╗")
                    .replace("│", "┊")
                    .replace("└───────┘", "╚┄┄┄┄┄┄┄╝")
                )
            design = updated_design
        elif dashed_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌───────┐", "╭┄┄┄┄┄┄┄╮")
                    .replace("│", "┊")
                    .replace("└───────┘", "╰┄┄┄┄┄┄┄╯")
                )
            design = updated_design
        elif fancy_design:
            updated_design = []
            for line in design:
                updated_design.append(line
                    .replace("┌───────┐", "╔ • • • ╗")
                    .replace("│", "•")
                    .replace("└───────┘", "╚ • • • ╝")
                )
            design = updated_design
        
        result = design[:1]
        
        for line in design[1:-2]:
            result.append(f"{line[0]}{self.suit.color}{line[1:-1]}\033[0m{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{self.suit.color}{design[-1]}\033[0m")
        
        return result
    
    class Back:
        def ascii():
            GRAY = "\033[90m"
            return [
                f"┌───────┐",
                f"│ {GRAY}><><>\033[0m │",
                f"│ {GRAY}<><><\033[0m │",
                f"│ {GRAY}><><>\033[0m │",
                f"│ {GRAY}<><><\033[0m │",
                f"│ {GRAY}><><>\033[0m │",
                f"└───────┘",
                f"         "
            ]

def print_cards_in_line(*cards: Card, spacer = "   ", print_it = True, **kwargs):
    if cards:
        result = [[] for _ in range(len(cards[0].ascii()))]
        for card in cards:
            for i, line in enumerate(card.ascii(**kwargs)):
                result[i].append(line)
        result = [
            spacer.join(line)
            for line in result
        ]
        if print_it:
            print("\n".join(result))
        return result
    if print_it:
        print("\n" * 7)
    return []

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
    SHOWDOWN = "Showdown"
    
    @property
    def amount_of_cards(self):
        return {
            Phase.PREFLOP: 0,
            Phase.FLOP: 3,
            Phase.TURN: 1,
            Phase.RIVER: 1,
            Phase.SHOWDOWN: 0
        }[self]
    
    @property
    def next(self):
        return {
            Phase.PREFLOP: Phase.FLOP,
            Phase.FLOP: Phase.TURN,
            Phase.TURN: Phase.RIVER,
            Phase.RIVER: Phase.SHOWDOWN,
            Phase.SHOWDOWN: None,
        }[self]

class MoveType(Enum):
    CHECK = "Check"
    CALL = "Call"
    
    BET = "Bet"
    RAISE = "Raise"
    RERAISE = "Re-Raise"
    
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
        self.move: Move | None = None
    
    def do_move(self, move: Move):

        if isinstance(move.type, MoveType.CHECK):
            return True
        
        self.game.bet = self.bet
        self.game.history.append(Move(move_type, move.amount))
    
    @property
    def possible_moves(self) -> list[MoveType]:
        if not self.is_in:
            return []
        
        result = [MoveType.FOLD]
        to_call = max(0, self.game.bet - self.bet)
        
        if to_call == 0:
            result.append(MoveType.CHECK)
        elif self.money >= to_call:
            result.append(MoveType.CALL)
        
        if self.game.bet == 0:
            if self.money >= self.game.big_blind:
                result.append(MoveType.BET)
        else:
            min_raise_total = to_call + self.game.last_full_raise
            if self.money >= min_raise_total:
                if self.game.raises_in_round > 0:
                    result.append(MoveType.RERAISE)
                else:
                    result.append(MoveType.RAISE)
        
        return result

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
        self.history: list[Move] = []
        self.turn: int = 0
        
        self.players: list[Player] = list(players)
        for player in self.players:
            player.game = self
        
        self.phase: Phase = Phase.PREFLOP
        self.agressor: int = 0
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
            if self.phase.amount_of_cards > 0:
                self.community_cards += self.stack[-self.phase.amount_of_cards:]
                self.stack = self.stack[:-self.phase.amount_of_cards]
            
            for player in self.players:
                self.pool += player.bet
                player.bet = 0
            
            self.bet = 0
            self.last_full_raise = self.big_blind
            self.raises_in_round = 0

    def your_turn(self):
        self.turn += 1
        self.turn %= len(self.players)

    def play_move(self) -> bool:
        player = self.players[self.turn]
        move = player.move
        if move is None:
            return False
        
        try:
            player.do_move(move)
            player.move = None
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    
    def test_run():
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
            print_cards_in_line(*game.community_cards)
            
            print()
            
            print(f"{game.players[0].name} \033[32m{game.players[0].money}*\033[0m")
            print_cards_in_line(*game.players[0].cards)
            
            print()
            
            print(f"{game.players[1].name} \033[32m{game.players[1].money}*\033[0m")
            print_cards_in_line(*game.players[1].cards)
            
            game.players[0].do_move(Move(MoveType.BET, 10))
            
            game.next_phase()
            
            time.sleep(1)

    move_type = "Check"
    
    try:
        print(MoveType(move_type))
    except ValueError:
        print("nope")
