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
    ROYAL_FLUSH = 1      # X
    STRAIGHT_FLUSH = 2   # X
    FOUR_OF_A_KIND = 3   # X
    FULL_HOUSE = 4       # X
    FLUSH = 5            # X
    STRAIGHT = 6         # X
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
    amount: int = 0

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
        if move.type == MoveType.CHECK:
            self.game.logs.append(f"{self.name} checked")
            return True
        
        if move.type == MoveType.FOLD:
            self.game.logs.append(f"{self.name} folded")
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
        elif self.money >= to_call:
            result.append(MoveType.CALL)
        
        if self.game.bet == 0:
            if self.money >= self.game.big_blind:
                result.append(MoveType.BET)
        else:
            # tweaking:
            min_raise_total = to_call + self.game.last_full_raise
            if self.money >= min_raise_total:
                if self.game.raises_in_round > 0:
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
        
        # === THREE PAIR ===================
        
        for i1, card1 in enumerate(hand_cards):
            for i2, card2 in enumerate(hand_cards[i1 + 1:]):
                for card3 in hand_cards[i1 + 1 + i2 + 1:]:
                    if card1.rank == card2.rank and card1.rank == card3.rank:
                        hand = Hand(HandRank.THREE_OF_A_KIND, [card1, card2, card3])
                        result.append(hand)
        
        # =================================
        
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
            
            self.last_full_raise = self.big_blind
            self.raises_in_round = 0

    def your_turn(self):
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
    def winner(self) -> int:
        RESET = "\033[0m"
        
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        GRAY = "\033[90m"

        print("==============")
        for player in self.players:
            for hand in player.hands:
                cards = [
                    f"{card.rank.value}{card.suit.value}"
                    for card in hand.cards
                ]
                color = {
                    HandRank.HIGH_CARD: "",
                    HandRank.PAIR: BLUE,
                    HandRank.TWO_PAIR: GREEN,
                    HandRank.THREE_OF_A_KIND: RED,
                }[hand.rank]
                print(f"{color}{hand.rank} ({', '.join(cards)}){RESET}")
            print("==============")
        
        return None

if __name__ == "__main__":
    print("Hello World!")