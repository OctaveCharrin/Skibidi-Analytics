import unittest

from skibidi.card import Card
from skibidi.dealer import Dealer


class TestDealer(unittest.TestCase):
    """Unit test suite for the Dealer class."""

    def setUp(self):
        """Set up a new game and dealer for each test."""
        self.hand_size = 5
        self.treasure_size = 3
        self.n_players = 4
        self.dealer = Dealer(hand_size=self.hand_size, treasure_size=self.treasure_size)

    def test_initialization(self):
        """Test that the dealer initializes with the correct state."""
        self.assertEqual(len(self.dealer.deck), 54, "Deck should have 54 cards.")
        self.assertEqual(
            len(self.dealer.draw_pile), 54, "Draw pile should start with 54 cards."
        )
        self.assertEqual(
            len(self.dealer.discard_pile), 0, "Discard pile should be initially empty."
        )
        self.assertEqual(
            len(self.dealer.treasure), 0, "Treasure should be initially empty."
        )
        self.assertEqual(self.dealer.view.draw_pile_size, 54)
        self.assertIs(self.dealer.view.discard_pile, self.dealer.discard_pile)

    def test_reset_deck(self):
        """Test that resetting the deck shuffles and resets all piles."""
        # Modify the state
        self.dealer.draw_pile = self.dealer.draw_pile[:10]
        self.dealer.discard_pile.append(Card(Card.Suit.SPADES, Card.Rank.ACE))

        # Keep a copy of the draw pile before reset to check for shuffling
        original_draw_pile_order = self.dealer.draw_pile[:]

        self.dealer.reset_deck()

        self.assertEqual(len(self.dealer.draw_pile), 54)
        self.assertEqual(len(self.dealer.discard_pile), 0)
        self.assertEqual(len(self.dealer.treasure), 0)

        # Check that the deck is actually shuffled (highly likely to be different)
        self.assertNotEqual(self.dealer.draw_pile, original_draw_pile_order)
        self.assertEqual(self.dealer.view.draw_pile_size, 54)

    def test_deal_initial_hands(self):
        """Test the initial dealing of cards to players."""
        player_names = [f"Player {i+1}" for i in range(self.n_players)]
        hands = {name: [] for name in player_names}

        self.dealer.deal_initial_hands(hands)

        # Check hand sizes
        for name in player_names:
            self.assertEqual(len(hands[name]), self.hand_size)

        # Check treasure size
        self.assertEqual(len(self.dealer.treasure), self.treasure_size)

        # Check discard pile
        self.assertEqual(len(self.dealer.discard_pile), 1)

        # Check remaining draw pile size
        expected_draw_pile_size = (
            54 - (self.n_players * self.hand_size) - self.treasure_size - 1
        )
        self.assertEqual(len(self.dealer.draw_pile), expected_draw_pile_size)
        self.assertEqual(self.dealer.view.draw_pile_size, expected_draw_pile_size)

    def test_deal_not_enough_cards(self):
        """Test that dealing fails if there are not enough cards."""
        # Create a scenario with too many players for the deck size
        too_many_players = 20
        player_names = [f"Player {i+1}" for i in range(too_many_players)]
        hands = {name: [] for name in player_names}

        with self.assertRaises(ValueError):
            self.dealer.deal_initial_hands(hands)

    def test_reshuffle_discard_into_draw(self):
        """Test reshuffling the discard pile back into the draw pile."""
        self.dealer.draw_pile = []
        self.dealer.discard_pile = [
            Card(Card.Suit.SPADES, Card.Rank.TWO),
            Card(Card.Suit.HEARTS, Card.Rank.THREE),
            Card(Card.Suit.CLUBS, Card.Rank.FOUR),  # This will be the top card
        ]

        self.dealer.reshuffle_discard_into_draw()

        # The new draw pile should contain the bottom 2 cards
        self.assertEqual(len(self.dealer.draw_pile), 2)
        # The discard pile should only contain the previous top card
        self.assertEqual(len(self.dealer.discard_pile), 1)
        self.assertEqual(self.dealer.discard_pile[0].rank, Card.Rank.FOUR)

    def test_draw_from_draw_pile(self):
        """Test drawing a card from the draw pile."""
        initial_size = len(self.dealer.draw_pile)
        card = self.dealer.draw_from_draw()

        self.assertIsInstance(card, Card)
        self.assertEqual(len(self.dealer.draw_pile), initial_size - 1)
        self.assertEqual(self.dealer.view.draw_pile_size, initial_size - 1)

    def test_draw_from_empty_draw_pile_with_reshuffle(self):
        """Test that drawing from an empty draw pile triggers a reshuffle."""
        self.dealer.draw_pile = []
        self.dealer.discard_pile = [
            Card(Card.Suit.SPADES, Card.Rank.ACE),
            Card(Card.Suit.HEARTS, Card.Rank.KING),
        ]

        card = self.dealer.draw_from_draw()

        self.assertIsNotNone(card)
        self.assertEqual(
            len(self.dealer.draw_pile), 0
        )  # Only one card was available to be moved to draw pile
        self.assertEqual(len(self.dealer.discard_pile), 1)

    def test_draw_from_completely_empty_deck(self):
        """Test that drawing fails when both piles are empty."""
        self.dealer.draw_pile = []
        self.dealer.discard_pile = []

        with self.assertRaises(ValueError):
            self.dealer.draw_from_draw()

    def test_draw_from_discard(self):
        """Test drawing a card from the discard pile."""
        top_card = Card(Card.Suit.DIAMONDS, Card.Rank.JACK)
        self.dealer.discard_pile.append(top_card)

        card = self.dealer.draw_from_discard()

        self.assertEqual(card, top_card)
        self.assertEqual(len(self.dealer.discard_pile), 0)

    def test_draw_from_empty_discard(self):
        """Test that drawing from an empty discard pile fails."""
        with self.assertRaises(ValueError):
            self.dealer.draw_from_discard()

    def test_discard(self):
        """Test that discarding adds a card to the discard pile."""
        card_to_discard = Card(Card.Suit.SPADES, Card.Rank.TEN)
        self.dealer.discard(card_to_discard)

        self.assertEqual(len(self.dealer.discard_pile), 1)
        self.assertEqual(self.dealer.discard_pile[0], card_to_discard)


if __name__ == "__main__":
    unittest.main()
