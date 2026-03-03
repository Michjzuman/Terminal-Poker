import poker

poker.settings.old_design = True

def print_cards_in_line(*cards: poker.Card, spacer = "  ", print_it = True):
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

if __name__ == "__main__":
    import os
    os.system("clear; clear")
    
    print_cards_in_line(
        poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
        poker.Card(poker.Rank.KING, poker.Suit.CLUBS),
        poker.Card(poker.Rank.QUEEN, poker.Suit.SPADES),
        poker.Card(poker.Rank.JACK, poker.Suit.DIAMONDS)
    )