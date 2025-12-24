import random
from datetime import datetime

ALL_RANKS = [
    "2", "3", "4",
    "5", "6", "7",
    "8", "9", "10",
    "J", "Q", "K", "A"
]

ALL_SUITS = [
    "H", "S", "D", "C"
]

GAME_STATES = [
    {
        "name": "Flop",
        "cards_revealed": 3
    },
    {
        "name": "River",
        "cards_revealed": 1
    },
    {
        "name": "Turn",
        "cards_revealed": 1
    }
]

def find_hands(cards):
    def royal_flush():
        res = []
        for kind in ALL_SUITS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([ALL_RANKS.index(card[1]) for card in flush_cards], reverse=True)

            if set(flush_values) >= {8, 9, 10, 11, 12}:
                res.append({"have": True, "points": sum(flush_values)})
        return res 
    def flush():
        res = []
        checked_kinds = set()
        for kind in ALL_SUITS:
            if kind in checked_kinds:
                continue
            checked_kinds.add(kind)
            hand = {"have": False}
            count = 0
            points = []
            for card in cards:
                if card[0] == kind:
                    count += 1
                    points.append(ALL_RANKS.index(card[1]) + 2)
            if count >= 5:
                hand["have"] = True
                for i in range(count - 4):
                    hand["points"] = sum(sorted(points[i:i + 5], reverse=True))
                    res.append(hand)
        return res
    def ofAKind(n):
        res = []
        checked_values = set()
        for card in cards:
            if card[1] in checked_values:
                continue
            checked_values.add(card[1])
            hand = {"have": False}
            count = 0
            points = []
            for checkCard in cards:
                if checkCard[1] == card[1]:
                    count += 1
                    points.append(ALL_RANKS.index(card[1]) + 2)
                    if count >= n:
                        hand["have"] = True
            if hand["have"]:
                hand["points"] = sum(sorted(points, reverse=True)[:n])
                res.append(hand)
        return res
    def straight():
        res = []
        points = []
        sorted_cards = sorted(cards, key=lambda card: ALL_RANKS.index(card[1]))
        for i in range(len(sorted_cards) - 4):
            hand = {"have": False}
            for j in range(i, i + 5):
                points.append(ALL_RANKS.index(sorted_cards[j][1]) + 2)

            if sorted(points) == list(range(min(points), max(points) + 1)):
                hand["have"] = True
                hand["points"] = sum(sorted(points, reverse=True))
                res.append(hand)
        return res
    def straight_flush():
        res = []
        for kind in ALL_SUITS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([ALL_RANKS.index(card[1]) for card in flush_cards], reverse=True)

            for i in range(len(flush_values) - 4):
                hand = {"have": False}
                straight_values = flush_values[i:i + 5]

                if straight_values[0] - straight_values[-1] == 4:
                    hand["have"] = True
                    hand["points"] = sum(straight_values)
                    res.append(hand)
        return res
    def full_house():
        res = []
        three_of_a_kind = ofAKind(3)
        pair = ofAKind(2)

        for three in three_of_a_kind:
            for two in pair:
                if three["points"] // 3 != two["points"] // 2:
                    res.append({
                        "have": True,
                        "points": three["points"] + two["points"]
                    })
        return res
    def two_pair():
        res = []
        pairs = ofAKind(2)

        if len(pairs) >= 2:
            for i in range(len(pairs) - 1):
                for j in range(i + 1, len(pairs)):
                    res.append({
                        "have": True,
                        "points": pairs[i]["points"] + pairs[j]["points"]
                    })
        return res
    def high_card():
        res = []
        for card in cards:
            res.append({
                "have": True,
                "points": ALL_RANKS.index(card[1]) + 2
            })
        return res
    
    hands = [
        royal_flush(),
        straight_flush(),
        ofAKind(4),
        full_house(),
        flush(),
        straight(),
        ofAKind(3),
        two_pair(),
        ofAKind(2),
        high_card()
    ]
    names = [
        "Royal Flush", "Straight Flush", "Four Of A Kind",
        "Full House", "Flush", "Straight", "Three Of A Kind",
        "Two Pair", "Pair", "High Card"
    ]

    def sort_hands(hands):
        return sorted(hands, key=lambda x: (names.index(x['hand']), -x['points']))

    res = []
    for i, hand in enumerate(hands):
        for h in hand:
            if h["have"]:
                res.append({"hand": names[i], "points": h["points"]})

    return sort_hands(res)

class Player:
    def __init__(self, game):
        self.table_id = game.next_table_id
        self.name : str
        self.coins : int
        self.last_handshake : str

class Game:
    def __init__(self):
        self.state = 0
        self.next_table_id = 0
        
        self.stack = [
            (rank, suit)
            for rank in ALL_RANKS
            for suit in ALL_SUITS
        ]
        random.shuffle(self.stack)
        
        self.community_cards = self.stack[:sum([
            state["cards_revealed"]
            for state in GAME_STATES
        ][:self.state + 1])]
        self.state_name = GAME_STATES[self.state]["name"]
        
        self.players = [
            Player(self)
        ]
        
        self.chat = []
    
    def chat_message(self, message):
        self.chat.append(message)
    
    def handshake(self, table_id):
        for player in self.players:
            if player.table_id == table_id:
                player.last_handshake = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    print(find_hands([
        ("2", "C"), ("3", "C"), ("4", "C"),
        ("5", "C"), ("6", "C"), ("6", "D")
    ]))