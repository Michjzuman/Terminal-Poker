import poker

poker.settings.old_design = True

if __name__ == "__main__":
    import os
    os.system("clear; clear")
    
    poker.print_cards_in_line(
        poker.Card(poker.Rank.SEVEN, poker.Suit.HEARTS),
        poker.Card(poker.Rank.KING, poker.Suit.CLUBS),
        poker.Card(poker.Rank.QUEEN, poker.Suit.SPADES),
        poker.Card(poker.Rank.JACK, poker.Suit.DIAMONDS)
    )