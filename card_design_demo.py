import poker

for rank in list(poker.Rank):
    poker.print_cards_in_line(*[
        poker.Card(rank, suit)
        for suit in list(poker.Suit)
    ], round_design = True)