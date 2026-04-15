import unittest
from unittest.mock import patch

import poker


def card(rank: str, suit: str) -> poker.Card:
    return poker.Card(getattr(poker.Rank, rank), getattr(poker.Suit, suit))


class PokerRuleTests(unittest.TestCase):
    def test_hand_ranking_and_tiebreakers(self):
        stronger_pair = poker.evaluate_five_card_hand([
            card("ACE", "SPADES"),
            card("ACE", "HEARTS"),
            card("KING", "DIAMONDS"),
            card("QUEEN", "CLUBS"),
            card("JACK", "SPADES"),
        ])
        weaker_pair = poker.evaluate_five_card_hand([
            card("ACE", "DIAMONDS"),
            card("ACE", "CLUBS"),
            card("QUEEN", "DIAMONDS"),
            card("JACK", "CLUBS"),
            card("TEN", "SPADES"),
        ])

        wheel_straight = poker.evaluate_five_card_hand([
            card("ACE", "SPADES"),
            card("TWO", "HEARTS"),
            card("THREE", "DIAMONDS"),
            card("FOUR", "CLUBS"),
            card("FIVE", "SPADES"),
        ])
        royal_flush = poker.evaluate_five_card_hand([
            card("ACE", "SPADES"),
            card("KING", "SPADES"),
            card("QUEEN", "SPADES"),
            card("JACK", "SPADES"),
            card("TEN", "SPADES"),
        ])

        self.assertEqual(stronger_pair.rank, poker.HandRank.PAIR)
        self.assertEqual(stronger_pair.tiebreaker, (14, 13, 12, 11))
        self.assertEqual(weaker_pair.rank, poker.HandRank.PAIR)
        self.assertLess(weaker_pair.strength, stronger_pair.strength)
        self.assertIs(poker.sort_hands(stronger_pair, weaker_pair)[0], stronger_pair)

        self.assertEqual(wheel_straight.rank, poker.HandRank.STRAIGHT)
        self.assertEqual(wheel_straight.tiebreaker, (5,))
        self.assertEqual(royal_flush.rank, poker.HandRank.ROYAL_FLUSH)
        self.assertEqual(royal_flush.tiebreaker, (14,))

    def test_heads_up_blinds_and_button_action_order(self):
        button = poker.Player("Button", 100)
        big_blind = poker.Player("BigBlind", 100)
        game = poker.Game(button, big_blind)

        game.setup_blinds()
        game.start_betting_round(game.next_active_index(game.big_blind_index))

        self.assertEqual(game.button_index, 0)
        self.assertEqual(game.small_blind_index, 0)
        self.assertEqual(game.big_blind_index, 1)
        self.assertEqual(game.turn, 0)
        self.assertEqual(button.possible_moves, [
            poker.MoveType.FOLD,
            poker.MoveType.CALL,
            poker.MoveType.RAISE,
        ])
        self.assertEqual(big_blind.possible_moves, [
            poker.MoveType.FOLD,
            poker.MoveType.CHECK,
            poker.MoveType.BET,
        ])

    def test_three_way_betting_round_completes_after_call_call_check(self):
        players = [poker.Player(name, 100) for name in ["A", "B", "C"]]
        game = poker.Game(*players)

        with patch("poker.random.shuffle", lambda seq: None):
            game.deal_cards()

        self.assertEqual(game.turn, 0)
        self.assertEqual([player.name for player in game.pending_players], ["A", "B", "C"])

        players[0].move = poker.Move(poker.MoveType.CALL)
        self.assertTrue(game.play_move())
        self.assertEqual(game.turn, 1)
        self.assertEqual([player.name for player in game.pending_players], ["B", "C"])
        self.assertFalse(game.round_complete)

        players[1].move = poker.Move(poker.MoveType.CALL)
        self.assertTrue(game.play_move())
        self.assertEqual(game.turn, 2)
        self.assertEqual([player.name for player in game.pending_players], ["C"])
        self.assertFalse(game.round_complete)

        players[2].move = poker.Move(poker.MoveType.CHECK)
        self.assertTrue(game.play_move())
        self.assertTrue(game.round_complete)
        self.assertFalse(game.finished)
        self.assertEqual([move.type for move in game.history], [
            poker.MoveType.CALL,
            poker.MoveType.CALL,
            poker.MoveType.CHECK,
        ])

    def test_split_pot_splits_odd_chip_to_first_showdown_winner(self):
        button = poker.Player("Button", 100)
        other = poker.Player("Other", 100)
        game = poker.Game(button, other)

        board = [
            card("TWO", "HEARTS"),
            card("THREE", "DIAMONDS"),
            card("FOUR", "SPADES"),
            card("FIVE", "CLUBS"),
            card("SIX", "HEARTS"),
        ]
        game.community_cards = board
        button.cards = [card("ACE", "SPADES"), card("KING", "DIAMONDS")]
        other.cards = [card("QUEEN", "SPADES"), card("JACK", "DIAMONDS")]
        button.is_in = True
        other.is_in = True
        button.total_contribution = 0
        other.total_contribution = 0
        game.pool = 5

        game.finish_hand()

        self.assertTrue(game.finished)
        self.assertEqual(len(game.pots), 1)
        self.assertEqual(game.pots[0]["amount"], 5)
        self.assertEqual([player.name for player in game.pots[0]["winners"]], ["Other", "Button"])
        self.assertEqual(game.pots[0]["payouts"][0][1], 3)
        self.assertEqual(game.pots[0]["payouts"][1][1], 2)
        self.assertEqual(
            sorted((player.name, amount) for player, amount in game.payouts),
            [("Button", 2), ("Other", 3)],
        )
        self.assertEqual(other.money, 103)
        self.assertEqual(button.money, 102)

    def test_fold_win_awards_blinds_without_showdown_hand(self):
        button = poker.Player("Button", 100)
        big_blind = poker.Player("BigBlind", 100)
        game = poker.Game(button, big_blind)

        game.deal_cards()
        button.move = poker.Move(poker.MoveType.FOLD)
        self.assertTrue(game.play_move())

        self.assertTrue(game.finished)
        self.assertEqual([(player.name, amount) for player, amount in game.payouts], [
            ("BigBlind", 3),
        ])
        self.assertEqual([pot["amount"] for pot in game.pots], [2, 1])
        self.assertTrue(all(pot["winning_hand"] is None for pot in game.pots))
        self.assertEqual((button.money, big_blind.money), (99, 101))

    def test_side_pots_award_each_pot_to_correct_winner(self):
        p1 = poker.Player("P1", 100)
        p2 = poker.Player("P2", 100)
        p3 = poker.Player("P3", 100)
        game = poker.Game(p1, p2, p3)

        game.community_cards = [
            card("TWO", "HEARTS"),
            card("THREE", "HEARTS"),
            card("FOUR", "HEARTS"),
            card("FIVE", "HEARTS"),
            card("NINE", "CLUBS"),
        ]
        p1.cards = [card("ACE", "HEARTS"), card("KING", "HEARTS")]
        p2.cards = [card("SIX", "SPADES"), card("SEVEN", "DIAMONDS")]
        p3.cards = [card("QUEEN", "CLUBS"), card("JACK", "SPADES")]

        for player, contribution in [(p1, 10), (p2, 20), (p3, 20)]:
            player.is_in = True
            player.total_contribution = contribution

        game.pool = 50
        game.finish_hand()

        self.assertEqual([pot["amount"] for pot in game.pots], [30, 20])
        self.assertEqual([[player.name for player in pot["winners"]] for pot in game.pots], [
            ["P1"],
            ["P2"],
        ])
        self.assertEqual([(player.name, amount) for player, amount in game.payouts], [
            ("P1", 30),
            ("P2", 20),
        ])
        self.assertEqual((p1.money, p2.money, p3.money), (130, 120, 100))


if __name__ == "__main__":
    unittest.main()
