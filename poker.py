#
# poker.py
#
# Author:
# Micha Wüthrich
#
# Note:
# Import this file as a python library if you want to play around with the poker game logic.
#


from enum import Enum
from dataclasses import dataclass
import random
import platform
from collections import Counter
from itertools import combinations

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
    owner: "Player" = None
    
    @property
    def points(self) -> list[int]:
        
        of_a_kind = [
            HandRank.HIGH_CARD, HandRank.PAIR,
            HandRank.THREE_OF_A_KIND, HandRank.FOUR_OF_A_KIND
        ]
        
        sum_valued = [
            HandRank.STRAIGHT, HandRank.FLUSH,
            HandRank.STRAIGHT_FLUSH, HandRank.ROYAL_FLUSH
        ]
        
        if any([self.rank is rank for rank in of_a_kind]):
            return [self.cards[0].rank.number]
        
        elif self.rank is HandRank.TWO_PAIR:
            c = sorted(self.cards, key=lambda c: c.rank.number)
            return [
                c[0].rank.number,
                c[-1].rank.number
            ]
        
        elif self.rank is HandRank.FULL_HOUSE:
            return [self.cards[0].rank.number * 15 + self.cards[3].rank.number]
        
        elif (
            any([self.rank is rank for rank in [HandRank.STRAIGHT, HandRank.STRAIGHT_FLUSH]])
            and any([card.rank.value == "A" for card in self.cards])
            and any([card.rank.value == "2" for card in self.cards])
        ):
            return [1 + 2 + 3 + 4 + 5]
        
        elif any([self.rank is rank for rank in sum_valued]):
            return [sum([
                card.rank.number
                for card in self.cards
            ])]
        
        return 67

    def is_egual(self, other: "Hand"):
        return (
            other.rank == self.rank and
            other.points == self.points
        )

def sort_hands(*hands: list[Hand]) -> list[Hand]:
    
    result = []
    
    for hand in hands:
        found = False
        
        for i, position in enumerate(result):
            if hand.rank.value < position.rank.value:
                result.insert(i, hand)
                found = True
                break
            
            elif hand.rank.value == position.rank.value:
                if hand.points[0] > position.points[0]:
                    result.insert(i, hand)
                    found = True
                    break
                elif hand.points[0] == position.points[0]:
                    if len(hand.points) <= 1 or hand.points[1] > position.points[1]:
                        result.insert(i, hand)
                        found = True
                        break
        
        if not found:
            result.append(hand)
    
    return result

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
    
    def do_move(self, move: Move):
        if move.type == MoveType.CHECK:
            self.game.logs.append(f"{self.name} checked")
            self.game.history.append(move)
            return True
        
        if move.type == MoveType.FOLD:
            self.game.logs.append(f"{self.name} folded")
            self.game.history.append(move)
            self.is_in = False
            return True
        
        diff = self.game.bet - self.bet + move.amount
        
        log = {
            MoveType.CALL: f"{self.name} called",
            MoveType.BET: f"{self.name} bet {move.amount}*",
            MoveType.RAISE: f"{self.name} raised by {move.amount}*",
            MoveType.RERAISE: f"{self.name} re-raised by {move.amount}*"
        }[move.type]
        
        
        if self.money >= diff:
            self.bet += diff
            self.money -= diff
            
            self.game.logs.append(log)
            self.game.history.append(move)
            
            return True
        else:
            return False
    
    @property
    def possible_moves(self) -> list[MoveType]:
        if not self.is_in:
            return []
        
        result = [MoveType.FOLD]
        
        
        to_call = max(0, self.game.bet - self.bet)
        
        if to_call == 0:

            result.append(MoveType.CHECK)
            result.append(MoveType.BET)
    
        elif self.money >= to_call:

            result.append(MoveType.CALL)
            
            last_move = self.game.history[-1].type
            if last_move is MoveType.RAISE or last_move is MoveType.RERAISE:
                result.append(MoveType.RERAISE)
            else:
                result.append(MoveType.RAISE)

        
        return result

    @property
    def hands(self) -> list[Hand]:
        hand_cards = self.cards + self.game.community_cards
        result = []
        
        # === HIGH CARD ===================
        
        for card in hand_cards:
            result.append(Hand(HandRank.HIGH_CARD, [card]))
        
        # === PAIR ========================
        
        pairs = []
        for i, card1 in enumerate(hand_cards):
            for card2 in hand_cards[i + 1:]:
                if card1.rank == card2.rank:
                    hand = Hand(HandRank.PAIR, [card1, card2])
                    pairs.append(hand)
                    result.append(hand)
        
        # === TWO PAIR ====================
        
        if len(pairs) >= 2:
            for i, pair1 in enumerate(pairs[:-1]):
                for pair2 in pairs[i + 1:]:
                    result.append(Hand(HandRank.TWO_PAIR, pair1.cards + pair2.cards))
        
        # === THREE OF A KIND =============
        
        three_of_a_kinds = []
        for i1, card1 in enumerate(hand_cards):
            for i2, card2 in enumerate(hand_cards[i1 + 1:]):
                for card3 in hand_cards[i1 + i2 + 2:]:
                    if card1.rank == card2.rank and card1.rank == card3.rank:
                        hand = Hand(HandRank.THREE_OF_A_KIND, [card1, card2, card3])
                        result.append(hand)
                        three_of_a_kinds.append(hand)
        
        # === STRAIGHT ====================
        
        straights = []
        ranks = sorted(hand_cards, key=lambda c: c.rank.number)
        all_ranks = [Rank.ACE.number] + [rank.number for rank in list(Rank)]
        for i, rank1 in enumerate(all_ranks[:-4]):
            straight = all_ranks[i:i+5]
            cards = []
            for rank in straight:
                rank_numbers = [r.rank.number for r in ranks]
                if rank in rank_numbers:
                    cards.append(ranks[rank_numbers.index(rank)])

            if len(cards) == 5:
                hand = Hand(HandRank.STRAIGHT, cards)
                result.append(hand)
                straights.append(hand)
        
        # === FLUSH =======================
        
        flushes = []
        for i1, card1 in enumerate(hand_cards):
            for i2, card2 in enumerate(hand_cards[i1 + 1:]):
                for i3, card3 in enumerate(hand_cards[i1 + i2 + 2:]):
                    for i4, card4 in enumerate(hand_cards[i1 + i2 + i3 + 3:]):
                        for card5 in hand_cards[i1 + i2 + i3 + i4 + 4:]:
                            cards = [card1, card2, card3, card4, card5]
                            if all(card.suit == cards[0].suit for card in cards):
                                hand = Hand(HandRank.FLUSH, cards)
                                result.append(hand)
                                flushes.append(hand)
        
        # === FULL HOUSE ==================
        
        if len(pairs) > 0 and len(three_of_a_kinds) > 0:
            for three_of_a_kind in three_of_a_kinds:
                for pair in pairs:
                    cards = three_of_a_kind.cards + pair.cards
                    if not any([
                        card1 == card2
                        for card1 in three_of_a_kind.cards
                        for card2 in pair.cards
                    ]):
                        result.append(Hand(HandRank.FULL_HOUSE, cards))
        
        # === FOUR OF A KIND =============
        
        for i1, card1 in enumerate(hand_cards):
            for i2, card2 in enumerate(hand_cards[i1 + 1:]):
                for i3, card3 in enumerate(hand_cards[i1 + i2 + 2:]):
                    for card4 in hand_cards[i1 + i2 + i3 + 3:]:
                        cards = [card1, card2, card3, card4]
                        if all(card.rank == cards[0].rank for card in cards):
                            hand = Hand(HandRank.FOUR_OF_A_KIND, cards)
                            result.append(hand)
                            three_of_a_kinds.append(hand)
        
        # === STRAIGHT / ROYAL FLUSH =====
        
        if len(straights) > 0 and len(flushes) > 0:
            for straight in straights:
                for flush in flushes:
                    straight_cards = sorted([
                        straight_card.rank.number
                        for straight_card in straight.cards
                    ])
                    flush_cards = sorted([
                        flush_card.rank.number
                        for flush_card in flush.cards
                    ])
                    if flush_cards == straight_cards:
                        ranks = [
                            flush_card.rank.value
                            for flush_card in flush.cards
                        ]
                        result.append(Hand(
                            HandRank.ROYAL_FLUSH
                            if "A" in ranks and "K" in ranks else
                            HandRank.STRAIGHT_FLUSH,
                            sorted(straight.cards, key=lambda c: c.rank.number)
                        ))
        
        # =================================
        
        for hand in result:
            hand.owner = self
        
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
        self.logs: list[str] = []
        
        self.players: list[Player] = list(players)
        for player in self.players:
            player.game = self
        
        self.phase: Phase = Phase.PREFLOP
        self.agressor: int = 0
        self.pool: int = pool
    
    @property
    def bet(self) -> int:
        return max([player.bet for player in self.players])
    
    def deal_cards(self) -> None:
        random.shuffle(self.stack)
        for player in self.players:
            player.cards += self.stack[-2:]
            self.stack = self.stack[:-2]
    
    def next_phase(self) -> None:
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
            
            self.last_full_raise = self.big_blind
            self.raises_in_round = 0

    def your_turn(self) -> None:
        for _ in range(len(self.players)):
            self.turn += 1
            self.turn %= len(self.players)
            if self.players[self.turn].is_in:
                break

    def play_move(self) -> bool:
        player = self.players[self.turn]
        move = player.move
        if move is None:
            return False
        
        try:
            if player.do_move(move):
                self.history.append(move)
                player.move = None
                self.your_turn()
                return True
            else:
                return False
        except ValueError:
            return False

    @property
    def winners(self) -> list[Player]:

        all_hands = []
        
        for player in self.players:
            all_hands += player.hands
        
        sorted_hands = sort_hands(*all_hands)
        
        if sorted_hands:
            
            possible_winners = self.players.copy()
            
            for hand in sorted_hands:
                if hand.owner in possible_winners:
                    for player in self.players:
                        if player != hand.owner and player in possible_winners:
                            if not any([hand.is_egual(other_hand) for other_hand in player.hands]):
                                possible_winners.remove(player)
                
                if len(possible_winners) == 0:
                    return possible_winners
            
            return possible_winners
        else:
            return [None]

if __name__ == "__main__":
    try:
        import test
    except ModuleNotFoundError:
        print("Hello World!")
