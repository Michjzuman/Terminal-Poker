#
# poker.py
#
# Author:
# Micha Wüthrich
#
# Note:
# Import this file as a python library if you want to play around with the poker game logic.
#


from collections import Counter
from enum import Enum
from dataclasses import dataclass
from itertools import combinations
import random
import platform

IS_MACOS = platform.system() == "Darwin"

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
    class DesignOption(Enum):
        OLD_DESIGN = "old"
        BORING_DESIGN = "boring"
        ROUND_DESIGN = "round"
        THICK_DESIGN = "thick"
        ROYAL_DESIGN = "royal"
        DASHED_DESIGN = "dashed"
        FANCY_DESIGN = "fancy"

    def __init__(self, rank: Rank, suit: Suit):
        self.rank: Rank = rank
        self.suit: Suit = suit
    
    def apply_design_option(text: list[str], design_option: DesignOption):
        if design_option == Card.DesignOption.OLD_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌───────┐", "+-------+")
                    .replace("│", "|")
                    .replace("└───────┘", "+-------+")
                )
            return updated_design
        elif design_option == Card.DesignOption.ROUND_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌", "╭")
                    .replace("└", "╰")
                    .replace("┐", "╮")
                    .replace("┘", "╯")
                )
            return updated_design
        elif design_option == Card.DesignOption.THICK_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌───────┐", "╔═══════╗")
                    .replace("│", "║")
                    .replace("└───────┘", "╚═══════╝")
                )
            return updated_design
        elif design_option == Card.DesignOption.ROYAL_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌───────┐", "╔┄┄┄┄┄┄┄╗")
                    .replace("│", "┊")
                    .replace("└───────┘", "╚┄┄┄┄┄┄┄╝")
                )
            return updated_design
        elif design_option == Card.DesignOption.DASHED_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌───────┐", "╭┄┄┄┄┄┄┄╮")
                    .replace("│", "┊")
                    .replace("└───────┘", "╰┄┄┄┄┄┄┄╯")
                )
            return updated_design
        elif design_option == Card.DesignOption.FANCY_DESIGN:
            updated_design = []
            for line in text:
                updated_design.append(line
                    .replace("┌───────┐", "╔ • • • ╗")
                    .replace("│", "•")
                    .replace("└───────┘", "╚ • • • ╝")
                )
            return updated_design
        return text

    def ascii(self, design_option: DesignOption = DesignOption.ROUND_DESIGN, **kwargs):
        
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
        
        design = Card.apply_design_option(design, design_option)
        
        result = design[:1]
        
        for line in design[1:-2]:
            result.append(f"{line[0]}{self.suit.color}{line[1:-1]}\033[0m{line[-1]}")
        
        result += design[-2:-1]
        result.append(f"{self.suit.color}{design[-1]}\033[0m")
        
        return result
    
    class Back:
        class DesignOption(Enum):
            A = "A"
            B = "B"
            C = "C"
            D = "D"
            SS = "67"
            HACKER = "hacker"
            if IS_MACOS:
                APPLE = "apple"
        
        def ascii(back_design_option: DesignOption = DesignOption.A, design_option = None):
            GRAY = "\033[90m"
            GREEN = "\033[32m"
            RESET = "\033[0m"
            
            design = [
                f"┌───────┐",
                f"│ {GRAY}><><>\033[0m │",
                f"│ {GRAY}<><><\033[0m │",
                f"│ {GRAY}><><>\033[0m │",
                f"│ {GRAY}<><><\033[0m │",
                f"│ {GRAY}><><>\033[0m │",
                f"└───────┘",
                f"         "
            ]
            if back_design_option == Card.Back.DesignOption.B:
                design = [
                    f"┌───────┐",
                    f"│ {GRAY}~ ~ ~\033[0m │",
                    f"│ {GRAY}~ ~ ~\033[0m │",
                    f"│ {GRAY}~ ~ ~\033[0m │",
                    f"│ {GRAY}~ ~ ~\033[0m │",
                    f"│ {GRAY}~ ~ ~\033[0m │",
                    f"└───────┘",
                    f"         "
                ]
            elif back_design_option == Card.Back.DesignOption.SS:
                design = [
                    f"┌───────┐",
                    f"│ {GRAY}.....\033[0m │",
                    f"│ {GRAY}.\033[0m6{GRAY}...\033[0m │",
                    f"│ {GRAY}.....\033[0m │",
                    f"│ {GRAY}...\033[0m7{GRAY}.\033[0m │",
                    f"│ {GRAY}.....\033[0m │",
                    f"└───────┘",
                    f"         "
                ]
            elif back_design_option == Card.Back.DesignOption.HACKER:
                design = [
                    f"┌───────┐"
                ] + [
                    f"│ {''.join([f'{GREEN if random.random() < 0.1 else GRAY}{random.randint(0, 1)}{RESET}' for _ in range(5)])} │"
                    for _ in range(5)
                ] + [
                    f"└───────┘",
                    f"         "
                ]
            elif back_design_option == Card.Back.DesignOption.C:
                design = [
                    f"┌───────┐",
                    f"│ {GRAY}/\/\/ \033[0m│",
                    f"│ {GRAY}\/\/\ \033[0m│",
                    f"│ {GRAY}/\/\/ \033[0m│",
                    f"│ {GRAY}\/\/\ \033[0m│",
                    f"│ {GRAY}/\/\/ \033[0m│",
                    f"└───────┘",
                    f"         "
                ]
            elif IS_MACOS and back_design_option == Card.Back.DesignOption.APPLE:
                design = [
                    f"┌───────┐",
                    f"│{GRAY} ~ ~ ~ \033[0m│",
                    f"│{GRAY} ~ ~ ~ \033[0m│",
                    f"│{GRAY} ~ \033[0m{GRAY} ~ \033[0m│",
                    f"│{GRAY} ~ ~ ~ \033[0m│",
                    f"│{GRAY} ~ ~ ~ \033[0m│",
                    f"└───────┘",
                    f"         "
                ]
            elif back_design_option == Card.Back.DesignOption.D:
                design = [
                    f"┌───────┐",
                    f"│ {GRAY}#####{RESET} │",
                    f"│ {GRAY}#####{RESET} │",
                    f"│ {GRAY}#####{RESET} │",
                    f"│ {GRAY}#####{RESET} │",
                    f"│ {GRAY}#####{RESET} │",
                    f"└───────┘",
                    f"         "
                ]
            
            return Card.apply_design_option(design, design_option)

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
    
    @property
    def name(self) -> str:
        return {
            HandRank.ROYAL_FLUSH: "Royal Flush",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.FOUR_OF_A_KIND: "Four Of A Kind",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FLUSH: "Flush",
            HandRank.STRAIGHT: "Straight",
            HandRank.THREE_OF_A_KIND: "Three Of A Kind",
            HandRank.TWO_PAIR: "Two Pair",
            HandRank.PAIR: "Pair",
            HandRank.HIGH_CARD :"High Card"
        }[self]

@dataclass
class Hand:
    rank: HandRank
    cards: list[Card]
    tiebreaker: tuple[int, ...]
    owner: "Player" = None
    
    @property
    def points(self) -> list[int]:
        return list(self.tiebreaker)

    @property
    def strength(self) -> tuple[int, ...]:
        return (len(HandRank) + 1 - self.rank.value, *self.tiebreaker)

    def is_equal(self, other: "Hand"):
        return (
            other.rank == self.rank and
            other.tiebreaker == self.tiebreaker
        )

    def is_egual(self, other: "Hand"):
        return self.is_equal(other)

def sort_hands(*hands: Hand) -> list[Hand]:
    return sorted(hands, key=lambda hand: hand.strength, reverse=True)

def straight_high_value(cards: list[Card]) -> int | None:
    ranks = sorted({card.rank.number for card in cards})
    if len(ranks) != 5:
        return None
    if ranks == [2, 3, 4, 5, 14]:
        return 5
    if ranks[-1] - ranks[0] == 4:
        return ranks[-1]
    return None

def ordered_straight_cards(cards: list[Card], straight_high: int) -> list[Card]:
    ordered_ranks = (
        [5, 4, 3, 2, 14]
        if straight_high == 5 else
        list(range(straight_high, straight_high - 5, -1))
    )
    remaining = list(cards)
    ordered = []
    for rank in ordered_ranks:
        for i, card in enumerate(remaining):
            if card.rank.number == rank:
                ordered.append(remaining.pop(i))
                break
    return ordered

def evaluate_five_card_hand(cards: tuple[Card, ...] | list[Card]) -> Hand:
    cards = list(cards)
    rank_numbers = [card.rank.number for card in cards]
    counts = Counter(rank_numbers)
    items_by_count = sorted(
        counts.items(),
        key=lambda item: (item[1], item[0]),
        reverse=True
    )
    flush = len({card.suit for card in cards}) == 1
    straight_high = straight_high_value(cards)

    if flush and straight_high is not None:
        rank = (
            HandRank.ROYAL_FLUSH
            if straight_high == Rank.ACE.number and min(rank_numbers) == Rank.TEN.number else
            HandRank.STRAIGHT_FLUSH
        )
        return Hand(rank, ordered_straight_cards(cards, straight_high), (straight_high,))

    if 4 in counts.values():
        quad_rank = max(rank for rank, count in counts.items() if count == 4)
        kicker = max(rank for rank, count in counts.items() if count == 1)
        ordered = sorted(
            cards,
            key=lambda card: (counts[card.rank.number], card.rank.number),
            reverse=True
        )
        return Hand(HandRank.FOUR_OF_A_KIND, ordered, (quad_rank, kicker))

    if sorted(counts.values()) == [2, 3]:
        trip_rank = max(rank for rank, count in counts.items() if count == 3)
        pair_rank = max(rank for rank, count in counts.items() if count == 2)
        ordered = sorted(
            cards,
            key=lambda card: (counts[card.rank.number], card.rank.number),
            reverse=True
        )
        return Hand(HandRank.FULL_HOUSE, ordered, (trip_rank, pair_rank))

    if flush:
        ordered = sorted(cards, key=lambda card: card.rank.number, reverse=True)
        return Hand(
            HandRank.FLUSH,
            ordered,
            tuple(card.rank.number for card in ordered)
        )

    if straight_high is not None:
        return Hand(
            HandRank.STRAIGHT,
            ordered_straight_cards(cards, straight_high),
            (straight_high,)
        )

    if 3 in counts.values():
        trip_rank = max(rank for rank, count in counts.items() if count == 3)
        kickers = sorted(
            [rank for rank, count in counts.items() if count == 1],
            reverse=True
        )
        ordered = sorted(
            cards,
            key=lambda card: (counts[card.rank.number], card.rank.number),
            reverse=True
        )
        return Hand(HandRank.THREE_OF_A_KIND, ordered, (trip_rank, *kickers))

    pair_ranks = sorted(
        [rank for rank, count in counts.items() if count == 2],
        reverse=True
    )
    if len(pair_ranks) == 2:
        kicker = max(rank for rank, count in counts.items() if count == 1)
        ordered = sorted(
            cards,
            key=lambda card: (counts[card.rank.number], card.rank.number),
            reverse=True
        )
        return Hand(HandRank.TWO_PAIR, ordered, (pair_ranks[0], pair_ranks[1], kicker))

    if len(pair_ranks) == 1:
        pair_rank = pair_ranks[0]
        kickers = sorted(
            [rank for rank, count in counts.items() if count == 1],
            reverse=True
        )
        ordered = sorted(
            cards,
            key=lambda card: (counts[card.rank.number], card.rank.number),
            reverse=True
        )
        return Hand(HandRank.PAIR, ordered, (pair_rank, *kickers))

    ordered = sorted(cards, key=lambda card: card.rank.number, reverse=True)
    return Hand(
        HandRank.HIGH_CARD,
        ordered,
        tuple(card.rank.number for card in ordered)
    )

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
    
    REVEAL_CARDS = "Reveal Cards"
    
    @property
    def requires_amount(self):
        return {
            MoveType.CHECK: False,
            MoveType.CALL: False,
            MoveType.BET: True,
            MoveType.RAISE: True,
            MoveType.RERAISE: True,
            MoveType.FOLD: False,
            MoveType.REVEAL_CARDS: False
        }[self]

@dataclass
class Move:
    type: MoveType
    amount: int = 0

class Player:
    def __init__(self, name: str, money: int):
        self.name: str = name
        self.money: int = money
        self.cards: list[Card] = []
        self.bet: int = 0
        self.is_in: bool = True
        self.game: "Game"
        self.move: Move = None
        self.winning_hand: Hand = None
        self.cards_revealed: bool = False
        self.is_all_in: bool = False
        self.total_contribution: int = 0

    def reset_for_round(self):
        self.cards = []
        self.bet = 0
        self.is_in = self.money > 0
        self.move = None
        self.winning_hand = None
        self.cards_revealed = False
        self.is_all_in = False
        self.total_contribution = 0

    def move_cost(self, move: Move) -> int:
        to_call = self.game.to_call(self)
        return to_call + (move.amount if move.type.requires_amount else 0)

    def commit_chips(self, amount: int) -> int:
        paid = min(amount, self.money)
        self.bet += paid
        self.money -= paid
        self.total_contribution += paid
        if self.is_in and self.money == 0:
            self.is_all_in = True
        return paid
    
    def do_move(self, move: Move):
        if move.type == MoveType.CHECK:
            self.game.logs.append(f"{self.name} -")
            self.game.written_logs.append(f"{self.name} checked")
            self.game.history.append(move)
            self.game.register_passive_action(self)
            return True
        
        if move.type == MoveType.FOLD:
            self.game.logs.append(f"{self.name} X")
            self.game.written_logs.append(f"{self.name} folded")
            self.game.history.append(move)
            self.cards = []
            self.is_in = False
            self.is_all_in = False
            self.game.register_passive_action(self)
            return True
        
        if move.type == MoveType.REVEAL_CARDS:
            cards_short = f"{' '.join([f'{card.rank.value}{card.suit.symbol}' for card in self.cards])}"
            self.game.logs.append(f"{self.name} = {cards_short}")
            self.game.written_logs.append(f"{self.name} revealed {cards_short}")
            self.game.history.append(move)
            self.cards_revealed = True
            return True
        
        to_call = self.game.to_call(self)
        previous_bet = self.game.bet

        if move.type == MoveType.CALL:
            paid = self.commit_chips(to_call)
            self.game.logs.append(f"{self.name} #")
            self.game.written_logs.append(
                f"{self.name} called {paid}*"
                if paid == to_call else
                f"{self.name} called all-in for {paid}*"
            )
            self.game.history.append(Move(move.type, paid))
            self.game.register_passive_action(self)
            return True

        diff = self.move_cost(move)
        if self.money < diff:
            return False

        previous_acted_players = set(self.game.acted_players)
        self.commit_chips(diff)

        actual_raise_size = max(0, self.bet - previous_bet)
        is_full_raise = (
            move.type == MoveType.BET or
            actual_raise_size >= self.game.last_full_raise
        )

        self.game.logs.append({
            MoveType.BET: f"{self.name} -> {move.amount}*",
            MoveType.RAISE: f"{self.name} -> +{actual_raise_size}*",
            MoveType.RERAISE: f"{self.name} -> +{actual_raise_size}*"
        }[move.type])
        self.game.written_logs.append({
            MoveType.BET: f"{self.name} bet {move.amount}*",
            MoveType.RAISE: f"{self.name} raised by {actual_raise_size}*",
            MoveType.RERAISE: f"{self.name} re-raised by {actual_raise_size}*"
        }[move.type])
        self.game.history.append(Move(move.type, actual_raise_size))
        self.game.register_aggressive_action(
            self,
            actual_raise_size,
            is_full_raise,
            previous_acted_players
        )
        return True
    
    @property
    def possible_moves(self) -> list[MoveType]:
        if not self.is_in or self.game.finished or self.game.round_complete or self.is_all_in:
            return []
        
        result = [MoveType.FOLD]
        
        to_call = self.game.to_call(self)
        
        if to_call == 0:
            result.append(MoveType.CHECK)
            if self.money > 0:
                result.append(MoveType.BET)
    
        else:
            result.append(MoveType.CALL)
            if self.game.can_raise(self):
                last_aggressive_move = self.game.last_aggressive_move_type
                result.append(
                    MoveType.RERAISE
                    if last_aggressive_move in [MoveType.RAISE, MoveType.RERAISE] else
                    MoveType.RAISE
                )

        
        return result

    @property
    def hands(self) -> list[Hand]:
        hand_cards = self.cards + self.game.community_cards
        if len(hand_cards) < 5:
            return []

        result = []
        for cards in combinations(hand_cards, 5):
            hand = evaluate_five_card_hand(cards)
            hand.owner = self
            result.append(hand)
        return result

    @property
    def best_hand(self) -> Hand | None:
        hands = self.hands
        if len(hands) == 0:
            return None
        return sort_hands(*hands)[0]

class Game:
    def __init__(self, *players: Player, pool: int = 0, small_blind: int = 1, big_blind: int = 2, beginner: int = 0):
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
        self.logs: list[str] = []
        self.written_logs: list[str] = []
        
        self.players: list[Player] = list(players)
        for player in self.players:
            player.game = self
        
        self.beginner: Player = self.players[beginner]
        
        self.phase: Phase = Phase.PREFLOP
        self.agressor: Player = self.players[beginner]
        self.pool: int = pool
        self.payouts: list[tuple[Player, int]] = []
        self.pots: list[dict] = []
        self.pot_awarded: bool = False
        self.button_index: int = beginner % len(self.players)
        self.small_blind_index: int = self.button_index
        self.big_blind_index: int = self.button_index
        self.pending_players: list[Player] = []
        self.acted_players: set[Player] = set()
        self.raise_restricted_players: set[Player] = set()
        self.round_complete: bool = False
        self.last_full_raise: int = self.big_blind
        self.last_aggressive_move_type: MoveType | None = None
    
    @property
    def bet(self) -> int:
        return max([player.bet for player in self.players], default=0)

    @property
    def active_players(self) -> list[Player]:
        return [player for player in self.players if player.is_in]

    def seat_order_from(self, start_index: int) -> list[Player]:
        return [
            self.players[(start_index + offset) % len(self.players)]
            for offset in range(len(self.players))
        ]

    def next_active_index(self, start_index: int) -> int:
        for offset in range(1, len(self.players) + 1):
            index = (start_index + offset) % len(self.players)
            if self.players[index].is_in:
                return index
        return start_index

    def to_call(self, player: Player) -> int:
        return max(0, self.bet - player.bet)

    def minimum_raise_amount(self, player: Player) -> int:
        to_call = self.to_call(player)
        remaining_after_call = max(0, player.money - to_call)
        if remaining_after_call <= 0:
            return 0
        if to_call == 0:
            return min(self.big_blind, remaining_after_call)
        if player in self.raise_restricted_players:
            return 0
        if remaining_after_call <= self.last_full_raise:
            return 1
        return self.last_full_raise

    def can_raise(self, player: Player) -> bool:
        return self.minimum_raise_amount(player) > 0

    def update_turn(self):
        if len(self.pending_players) > 0:
            self.turn = self.players.index(self.pending_players[0])
            self.round_complete = False
        else:
            self.round_complete = True

    def register_passive_action(self, player: Player):
        self.acted_players.add(player)
        self.pending_players = [
            pending_player for pending_player in self.pending_players
            if pending_player != player and pending_player.is_in and not pending_player.is_all_in
        ]
        self.update_turn()

    def register_aggressive_action(
        self,
        player: Player,
        raise_size: int,
        is_full_raise: bool,
        previous_acted_players: set[Player]
    ):
        self.agressor = player
        self.acted_players = {player}
        self.last_aggressive_move_type = self.history[-1].type
        if is_full_raise:
            self.last_full_raise = max(raise_size, self.big_blind if self.bet == player.bet else raise_size)
            self.raise_restricted_players = set()
        else:
            self.raise_restricted_players = {
                other_player for other_player in previous_acted_players
                if other_player != player and other_player.is_in and not other_player.is_all_in
            }

        start_index = (self.players.index(player) + 1) % len(self.players)
        self.pending_players = [
            pending_player for pending_player in self.seat_order_from(start_index)
            if pending_player.is_in and not pending_player.is_all_in and pending_player != player
        ]
        self.update_turn()

    def start_betting_round(self, start_index: int):
        self.acted_players = set()
        self.raise_restricted_players = set()
        self.round_complete = False
        self.pending_players = [
            player for player in self.seat_order_from(start_index)
            if player.is_in and not player.is_all_in
        ]
        self.update_turn()

    def post_blind(self, player: Player, amount: int, label: str):
        paid = player.commit_chips(amount)
        self.logs.append(f"{player.name} {label} {paid}*")
        self.written_logs.append(f"{player.name} posted {label} {paid}*")

    def setup_blinds(self):
        if len(self.players) == 2:
            self.small_blind_index = self.button_index
            self.big_blind_index = self.next_active_index(self.small_blind_index)
        else:
            self.small_blind_index = self.next_active_index(self.button_index)
            self.big_blind_index = self.next_active_index(self.small_blind_index)

        self.post_blind(self.players[self.small_blind_index], self.small_blind, "SB")
        self.post_blind(self.players[self.big_blind_index], self.big_blind, "BB")
        self.last_full_raise = self.big_blind
        self.last_aggressive_move_type = MoveType.BET
    
    def deal_cards(self) -> None:
        random.shuffle(self.stack)
        for player in self.players:
            player.cards += self.stack[-2:]
            self.stack = self.stack[:-2]
        self.setup_blinds()
        self.start_betting_round(self.next_active_index(self.big_blind_index))

    def collect_bets(self) -> None:
        for player in self.players:
            self.pool += player.bet
            player.bet = 0

    def eligible_players_for_pot(self, minimum_contribution: int) -> list[Player]:
        return [
            player for player in self.players
            if player.total_contribution >= minimum_contribution and player.is_in
        ]

    def build_pots(self) -> list[tuple[int, list[Player]]]:
        contributions = sorted({
            player.total_contribution
            for player in self.players
            if player.total_contribution > 0
        })
        previous_level = 0
        pots = []

        for level in contributions:
            contributors = [
                player for player in self.players
                if player.total_contribution >= level
            ]
            amount = (level - previous_level) * len(contributors)
            eligible_players = [
                player for player in contributors
                if player.is_in
            ]
            if amount > 0 and len(eligible_players) > 0:
                pots.append((amount, eligible_players))
            previous_level = level

        accounted_amount = sum(amount for amount, _ in pots)
        leftover_pool = self.pool - accounted_amount
        if leftover_pool > 0 and len(self.active_players) > 0:
            pots.append((leftover_pool, self.active_players))

        return pots

    def showdown_order(self) -> list[Player]:
        start_index = self.next_active_index(self.button_index)
        return [
            player for player in self.seat_order_from(start_index)
            if player.is_in
        ]

    def payout_winners(self) -> None:
        if self.pot_awarded:
            return

        self.payouts = []
        self.pots = []
        total_payouts: dict[Player, int] = {}
        showdown_order = self.showdown_order()

        for pot_index, (amount, eligible_players) in enumerate(self.build_pots(), start=1):
            comparable_hands = [
                player.best_hand
                for player in eligible_players
                if player.best_hand is not None
            ]

            if comparable_hands:
                winning_hand = sort_hands(*comparable_hands)[0]
                winning_players = [
                    player for player in eligible_players
                    if player.best_hand is not None and player.best_hand.is_equal(winning_hand)
                ]
            else:
                winning_hand = None
                winning_players = [player for player in eligible_players if player.is_in]

            ordered_winners = [
                player for player in showdown_order
                if player in winning_players
            ]
            if len(ordered_winners) == 0:
                ordered_winners = winning_players

            share = amount // len(ordered_winners)
            remainder = amount % len(ordered_winners)

            payouts = []
            for i, player in enumerate(ordered_winners):
                payout_amount = share + (1 if i < remainder else 0)
                player.money += payout_amount
                total_payouts[player] = total_payouts.get(player, 0) + payout_amount
                payouts.append((player, payout_amount))

            self.pots.append({
                "index": pot_index,
                "amount": amount,
                "winners": ordered_winners,
                "winning_hand": winning_hand,
                "payouts": payouts,
            })

        self.payouts = [
            (player, total_payouts[player])
            for player in self.players
            if total_payouts.get(player, 0) > 0
        ]
        for player, amount in self.payouts:
            self.logs.append(f"{player.name} <- {amount}*")
            self.written_logs.append(f"{player.name} won {amount}*")

        self.pot_awarded = True

    def finish_hand(self) -> None:
        if self.finished:
            return
        self.collect_bets()
        self.phase = Phase.SHOWDOWN
        for player in self.active_players:
            player.cards_revealed = True
            player.winning_hand = player.best_hand
        self.payout_winners()
        self.finished = True
        self.round_complete = True
        self.pending_players = []
    
    def next_phase(self) -> None:
        if self.finished:
            return

        if len(self.active_players) <= 1:
            self.finish_hand()
            return

        self.collect_bets()

        if self.phase == Phase.PREFLOP:
            self.phase = Phase.FLOP
        elif self.phase == Phase.FLOP:
            self.phase = Phase.TURN
        elif self.phase == Phase.TURN:
            self.phase = Phase.RIVER
        elif self.phase == Phase.RIVER:
            self.phase = Phase.SHOWDOWN
            self.finish_hand()
            return
        else:
            self.finish_hand()
            return

        if self.phase.amount_of_cards > 0:
            self.community_cards += self.stack[-self.phase.amount_of_cards:]
            self.stack = self.stack[:-self.phase.amount_of_cards]

        self.last_full_raise = self.big_blind
        self.last_aggressive_move_type = None
        self.agressor = self.players[self.button_index]
        self.start_betting_round(self.next_active_index(self.button_index))

    def your_turn(self) -> None:
        self.update_turn()

    def play_move(self) -> bool:
        if self.finished or self.round_complete:
            return False

        player = self.players[self.turn]
        move = player.move
        if move is None:
            return False

        player.move = None

        try:
            if player.do_move(move):
                active_players = [candidate for candidate in self.players if candidate.is_in]
                if len(active_players) <= 1:
                    if len(active_players) == 1:
                        winner = active_players[0]
                        self.turn = self.players.index(winner)
                        self.agressor = winner
                    self.finish_hand()
                    return True
                return True
            else:
                return False
        except ValueError:
            return False

    @property
    def winners(self) -> list[Player]:
        players_in_hand = [player for player in self.players if player.is_in]
        if len(players_in_hand) <= 1:
            return players_in_hand or [None]

        best_hands = [
            player.best_hand
            for player in players_in_hand
            if player.best_hand is not None
        ]
        sorted_best_hands = sort_hands(*best_hands)

        if len(sorted_best_hands) == 0:
            return [None]

        winning_hand = sorted_best_hands[0]
        return [
            player for player in players_in_hand
            if player.best_hand is not None and player.best_hand.is_equal(winning_hand)
        ]

if __name__ == "__main__":
    try:
        import test
    except ModuleNotFoundError:
        print("Hello World!")
