#
# card_design_demo.py
#
# Author:
# Micha Wüthrich
#
# Note:
# This file gives you a demo of the ASCII-Card designs i made for this game.
#

import poker

for design_option in reversed(list(poker.Card.DesignOption)):
    
    print(f"\n\033[32m=== {design_option.value.upper()}{' ===' * 20}\033[0m\n")

    for suit in list(poker.Suit):
        poker.print_cards_in_line(*[
            poker.Card(rank, suit)
            for rank in list(poker.Rank)
        ], design_option = design_option)

    backs = [
        poker.Card.Back.ascii(
            design_option = design_option,
            back_design_option = back_design_option
        )
        for back_design_option in list(poker.Card.Back.DesignOption)
    ]

    result = [[] for _ in range(len(backs[0]))]
    for card in backs:
        for i, line in enumerate(card):
            result[i].append(line)
    result = [
        "   ".join(line)
        for line in result
    ]
    print("\n".join(result))
