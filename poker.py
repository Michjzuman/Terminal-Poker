from enum import Enum
from dataclasses import dataclass
import random

class Settings:
    def __init__(self):
        self.old_design = False

settings = Settings()

class Rank(Enum):
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

def print_cards_in_line(*cards: Card, spacer = "   ", print_it = True):
    if cards:
        result = [[] for _ in range(len(cards[0].ascii))]
        for card in cards:
            for i, line in enumerate(card.ascii):
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

def compare_hands(*hands: list[Card]) -> list[int]:
    from collections import Counter
    from itertools import combinations

    if not hands:
        return []

    def evaluate_five(cards: tuple[Card, ...]):
        rank_values = sorted((card.rank.value for card in cards), reverse=True)
        counts = Counter(rank_values)
        grouped = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)

        is_flush = len({card.suit for card in cards}) == 1
        unique_ranks = sorted(set(rank_values), reverse=True)
        straight_high = 0
        if len(unique_ranks) == 5:
            if unique_ranks[0] - unique_ranks[-1] == 4:
                straight_high = unique_ranks[0]
            elif unique_ranks == [14, 5, 4, 3, 2]:
                straight_high = 5
        is_straight = straight_high > 0

        if is_flush and unique_ranks == [14, 13, 12, 11, 10]:
            HandRank = HandRank.ROYAL_FLUSH
            tie_break = ()
        elif is_flush and is_straight:
            HandRank = HandRank.STRAIGHT_FLUSH
            tie_break = (straight_high,)
        elif grouped[0][1] == 4:
            HandRank = HandRank.FOUR_OF_A_KIND
            tie_break = (grouped[0][0], grouped[1][0])
        elif grouped[0][1] == 3 and grouped[1][1] == 2:
            HandRank = HandRank.FULL_HOUSE
            tie_break = (grouped[0][0], grouped[1][0])
        elif is_flush:
            HandRank = HandRank.FLUSH
            tie_break = tuple(rank_values)
        elif is_straight:
            HandRank = HandRank.STRAIGHT
            tie_break = (straight_high,)
        elif grouped[0][1] == 3:
            HandRank = HandRank.THREE_OF_A_KIND
            kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
            tie_break = (grouped[0][0], *kickers)
        elif grouped[0][1] == 2 and grouped[1][1] == 2:
            HandRank = HandRank.TWO_PAIR
            high_pair = max(grouped[0][0], grouped[1][0])
            low_pair = min(grouped[0][0], grouped[1][0])
            kicker = max(rank for rank, count in counts.items() if count == 1)
            tie_break = (high_pair, low_pair, kicker)
        elif grouped[0][1] == 2:
            HandRank = HandRank.PAIR
            kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
            tie_break = (grouped[0][0], *kickers)
        else:
            HandRank = HandRank.HIGH_CARD
            tie_break = tuple(rank_values)

        return (11 - HandRank.value, *tie_break)

    def evaluate_hand(cards: list[Card]):
        if len(cards) >= 5:
            return max(evaluate_five(combo) for combo in combinations(tuple(cards), 5))

        rank_values = sorted((card.rank.value for card in cards), reverse=True)
        counts = Counter(rank_values)
        grouped = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
        pair_count = sum(1 for _, count in grouped if count == 2)

        if grouped and grouped[0][1] == 4:
            tie_break = (grouped[0][0], grouped[1][0] if len(grouped) > 1 else 0)
            return (11 - HandRank.FOUR_OF_A_KIND.value, *tie_break)
        if grouped and grouped[0][1] == 3:
            if len(grouped) > 1 and grouped[1][1] >= 2:
                return (11 - HandRank.FULL_HOUSE.value, grouped[0][0], grouped[1][0])
            kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
            return (11 - HandRank.THREE_OF_A_KIND.value, grouped[0][0], *kickers)
        if pair_count >= 2:
            pairs = sorted((rank for rank, count in counts.items() if count == 2), reverse=True)
            kicker = max((rank for rank, count in counts.items() if count == 1), default=0)
            return (11 - HandRank.TWO_PAIR.value, pairs[0], pairs[1], kicker)
        if pair_count == 1:
            pair = max(rank for rank, count in counts.items() if count == 2)
            kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
            return (11 - HandRank.PAIR.value, pair, *kickers)
        return (11 - HandRank.HIGH_CARD.value, *rank_values)

    scores = [evaluate_hand(list(hand)) for hand in hands]
    best = max(scores)
    return [index for index, score in enumerate(scores) if score == best]

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
            self.bet += self.game.bet
        
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
        if self.phase == Phase.TURN:
            self.finished = True
        else:
            self.phase = self.phase.next
            self.community_cards += self.stack[-self.phase.amount_of_cards:]
            self.stack = self.stack[:-self.phase.amount_of_cards]
            
            for player in self.players:
                self.pool += player.bet
                player.bet = 0


if __name__ == "__main__":
    import os
    import time
    
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
