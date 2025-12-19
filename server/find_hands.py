import rules

def find_hands(cards):
    def royal_flush():
        res = []
        for kind in rules.ALL_SUITS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([rules.ALL_RANKS.index(card[1]) for card in flush_cards], reverse=True)

            if set(flush_values) >= {8, 9, 10, 11, 12}:
                res.append({"have": True, "points": sum(flush_values)})
        return res 
    def flush():
        res = []
        checked_kinds = set()
        for kind in rules.ALL_SUITS:
            if kind in checked_kinds:
                continue
            checked_kinds.add(kind)
            hand = {"have": False}
            count = 0
            points = []
            for card in cards:
                if card[0] == kind:
                    count += 1
                    points.append(rules.ALL_RANKS.index(card[1]) + 2)
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
                    points.append(rules.ALL_RANKS.index(card[1]) + 2)
                    if count >= n:
                        hand["have"] = True
            if hand["have"]:
                hand["points"] = sum(sorted(points, reverse=True)[:n])
                res.append(hand)
        return res
    def straight():
        res = []
        points = []
        sorted_cards = sorted(cards, key=lambda card: rules.ALL_RANKS.index(card[1]))
        for i in range(len(sorted_cards) - 4):
            hand = {"have": False}
            for j in range(i, i + 5):
                points.append(rules.ALL_RANKS.index(sorted_cards[j][1]) + 2)

            if sorted(points) == list(range(min(points), max(points) + 1)):
                hand["have"] = True
                hand["points"] = sum(sorted(points, reverse=True))
                res.append(hand)
        return res
    def straight_flush():
        res = []
        for kind in rules.ALL_SUITS:
            flush_cards = [card for card in cards if card[0] == kind]
            flush_values = sorted([rules.ALL_RANKS.index(card[1]) for card in flush_cards], reverse=True)

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
                "points": rules.ALL_RANKS.index(card[1]) + 2
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

if __name__ == "__main__":
    print(find_hands([("2", "C"), ("3", "C"), ("4", "C"), ("5", "C"), ("6", "C"), ("6", "D"), ("6", "H")]))