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

for rank in list(poker.Rank):
    poker.print_cards_in_line(*[
        poker.Card(rank, suit)
        for suit in list(poker.Suit)
    ], round_design = True)