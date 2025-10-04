import unittest
from unittest.mock import MagicMock, patch

from skibidi.card import Card
from skibidi.dealer import Dealer
from skibidi.game import Game
from skibidi.player import Player
from skibidi.strategy import Strategy


class TestGame(unittest.TestCase):
    """Unit test suite for the Game class, excluding the play() method."""

    def setUp(self):
        """Set up a Game instance with real Player objects and mock strategies."""
        self.player_names = ["P1", "P2"]
        self.game = Game(n_players=2, names=self.player_names, hand_size=2, treasure_size=1)

        # Assign mock strategies to each player
        for player in self.game.players:
            player.strategy = MagicMock(spec=Strategy)

        # Pre-populate hands for testing
        self.card1 = Card(Card.Suit.HEARTS, Card.Rank.ACE)
        self.card2 = Card(Card.Suit.SPADES, Card.Rank.TWO)
        self.card3 = Card(Card.Suit.CLUBS, Card.Rank.THREE)
        self.card4 = Card(Card.Suit.DIAMONDS, Card.Rank.FOUR)
        self.game.hands["P1"] = [self.card1, self.card2]
        self.game.hands["P2"] = [self.card3, self.card4]

        # Initialize player views to match hand sizes
        for p in self.game.players:
            p.view.hand = [None] * len(self.game.hands[p.name])
            p.view.opponents_hands = {
                op.name: [None] * len(self.game.hands[op.name]) for op in self.game.players if op != p
            }


    def test_initialization(self):
        """Test that the Game is initialized correctly."""
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.players[0].name, "P1")
        self.assertEqual(len(self.game.hands), 2)
        self.assertIn("P1", self.game.hands)
        self.assertIn("P2", self.game.hands)
        self.assertIsInstance(self.game.dealer, Dealer)
        self.assertIsInstance(self.game.view, Game.View)

    def test_get_player_by_name(self):
        """Test retrieving a player by their name."""
        player1 = self.game.get_player_by_name("P1")
        self.assertEqual(player1.name, "P1")
        with self.assertRaises(ValueError):
            self.game.get_player_by_name("NonExistentPlayer")

    def test_discard_by_index(self):
        """Test discarding a card from a player's hand by index."""
        player1 = self.game.players[0]
        card_to_discard = self.game.hands[player1.name][0]
        
        self.game.discard(player1, idx=0)
        
        self.assertEqual(len(self.game.hands[player1.name]), 1)
        self.assertIn(card_to_discard, self.game.dealer.discard_pile)
        self.assertEqual(len(player1.view.hand), 1)

    def test_discard_by_card_object(self):
        """Test discarding a card that is not in hand (e.g., a drawn card)."""
        player1 = self.game.players[0]
        new_card = Card(None, Card.Rank.JOKER_RED)
        
        self.game.discard(player1, card=new_card)
        
        self.assertIn(new_card, self.game.dealer.discard_pile)
        self.assertIsNone(player1.view.drawn_card)

    def test_discard_queues_effect(self):
        """Test that discarding a card with an effect adds it to the queue."""
        player1 = self.game.players[0]
        effect_card = Card(Card.Suit.HEARTS, Card.Rank.JACK) # PEEK effect
        self.game.discard(player1, card=effect_card)
        
        self.assertIn((player1, Card.Effect.PEEK), self.game.view.effects_queue)

    def test_exchange(self):
        """Test exchanging a card in a player's hand."""
        player1 = self.game.players[0]
        old_card = self.game.hands[player1.name][0]
        new_card = Card(None, Card.Rank.JOKER_BLACK)

        returned_card = self.game.exchange(player1, 0, new_card)

        self.assertIs(returned_card, old_card)
        self.assertIs(self.game.hands[player1.name][0], new_card)
        # Check that the player's view was updated
        self.assertEqual(player1.view.hand[0], new_card)

    @patch('skibidi.dealer.Dealer.draw')
    def test_penalize(self, mock_draw):
        """Test that a player is penalized with a new card."""
        player1 = self.game.players[0]
        penalty_card = Card(Card.Suit.CLUBS, Card.Rank.TEN)
        mock_draw.return_value = penalty_card

        self.game.penalize(player1)

        self.assertEqual(len(self.game.hands[player1.name]), 3)
        self.assertIn(penalty_card, self.game.hands[player1.name])
        self.assertEqual(len(player1.view.hand), 3) # View should also be updated
        self.assertIsNone(player1.view.hand[-1])

    def test_reveal_to_others(self):
        """Test that a card is revealed to all other players."""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        card_to_reveal = self.game.hands[player1.name][0]

        self.game.reveal_to_others(player1, 0, card_to_reveal)
        # The opponent's view should have been updated to reflect the revealed card
        self.assertEqual(player2.view.opponents_hands[player1.name][0], card_to_reveal)

    def test_apply_effect_peek(self):
        """Test the PEEK effect."""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        
        # Player 1 wants to peek at Player 2's card at index 1
        decision = (player2.name, 1)
        card_to_peek = self.game.hands[player2.name][1]
        
        self.game.apply_effect(player1, Card.Effect.PEEK, decision)
        # The acting player's view should have learned the opponent's card
        self.assertEqual(player1.view.opponents_hands[player2.name][1], card_to_peek)

    @patch('random.shuffle')
    def test_apply_effect_shuffle(self, mock_shuffle):
        """Test the SHUFFLE effect."""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        
        # Player 1 shuffles Player 2's hand
        decision = player2.name
        self.game.apply_effect(player1, Card.Effect.SHUFFLE, decision)
        mock_shuffle.assert_called_once_with(self.game.hands[player2.name])
        # Check that player 2's view of their own hand is now unknown
        self.assertEqual(player2.view.hand, [None, None])

    def test_apply_effect_swap(self):
        """Test the SWAP effect."""
        p1_card = self.game.hands["P1"][0]
        p2_card = self.game.hands["P2"][1]
        
        decision = ("P1", 0, "P2", 1)
        self.game.apply_effect(self.game.players[0], Card.Effect.SWAP, decision)
        
        self.assertIs(self.game.hands["P1"][0], p2_card)
        self.assertIs(self.game.hands["P2"][1], p1_card)

    @patch('skibidi.game.Game.penalize')
    def test_apply_effect_draw(self, mock_penalize):
        """Test the DRAW effect."""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        
        decision = player2.name
        self.game.apply_effect(player1, Card.Effect.DRAW, decision)
        mock_penalize.assert_called_once_with(player2)

    def test_calculate_scores_success(self):
        """Test score calculation for a successful call."""
        self.game.caller_index = 0 # P1 is the caller
        self.game.hands["P1"] = [Card(Card.Suit.HEARTS, Card.Rank.TWO)] # Score 2
        self.game.hands["P2"] = [Card(Card.Suit.HEARTS, Card.Rank.THREE)] # Score 3

        self.game.calculate_scores()
        
        self.assertEqual(self.game.view.scores[0], 0) # Successful call, score is 0
        self.assertEqual(self.game.view.scores[1], 3)

    def test_calculate_scores_fail(self):
        """Test score calculation for a failed call."""
        self.game.caller_index = 0 # P1 is the caller
        self.game.hands["P1"] = [Card(Card.Suit.HEARTS, Card.Rank.FOUR)] # Score 4
        self.game.hands["P2"] = [Card(Card.Suit.HEARTS, Card.Rank.THREE)] # Score 3

        self.game.calculate_scores()
        
        self.assertEqual(self.game.view.scores[0], 8) # Failed call, score is 4 * 2
        self.assertEqual(self.game.view.scores[1], 3)

    @patch('skibidi.dealer.Dealer.deal_initial_hands')
    def test_init_round(self, mock_deal):
        """Test the initialization of a new round."""
        self.game.initially_known = [0] # Know the first card
        # We need to re-populate hands as init_round will clear them
        self.game.hands["P1"] = [self.card1, self.card2]
        self.game.hands["P2"] = [self.card3, self.card4]

        self.game.init_round()
        mock_deal.assert_called_once_with(self.game.hands)
        # Check that players' views were updated for the initially known cards
        self.assertEqual(self.game.players[0].view.hand[0], self.game.hands["P1"][0])
        self.assertEqual(self.game.players[1].view.hand[0], self.game.hands["P2"][0])

    def test_is_finished(self):
        """Test the game completion condition."""
        self.assertFalse(self.game.is_finished())
        self.game.view.scores[0] = 100
        self.assertTrue(self.game.is_finished())
        self.game.view.scores[0] = 99
        self.game.view.scores[1] = 101
        self.assertTrue(self.game.is_finished())

if __name__ == "__main__":
    unittest.main()
