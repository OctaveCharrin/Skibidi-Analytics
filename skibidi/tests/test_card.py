import unittest


from skibidi.card import Card

class TestCard(unittest.TestCase):
    """Binary test suite for the Card class."""

    def test_card_creation_and_attributes(self):
        """Tests that a standard card is created with the correct suit, rank, and effect."""
        card = Card(Card.Suit.SPADES, Card.Rank.ACE)
        self.assertEqual(card.suit, Card.Suit.SPADES)
        self.assertEqual(card.rank, Card.Rank.ACE)
        self.assertEqual(card.effect, Card.Effect.NONE, "Aces should have no effect.")

    def test_joker_creation(self):
        """Tests that a Joker is created correctly, with no suit."""
        joker = Card(None, Card.Rank.JOKER_RED)
        self.assertIsNone(joker.suit, "Jokers should have no suit.")
        self.assertEqual(joker.rank, Card.Rank.JOKER_RED)
        self.assertEqual(joker.effect, Card.Effect.NONE, "Jokers should have no effect.")

    def test_card_representation(self):
        """Tests the __repr__ method for both standard cards and Jokers."""
        card_10h = Card(Card.Suit.HEARTS, Card.Rank.TEN)
        self.assertEqual(repr(card_10h), "10♥")

        joker_b = Card(None, Card.Rank.JOKER_BLACK)
        self.assertEqual(repr(joker_b), "JOKER_BLACK")

    def test_card_equality(self):
        """Tests the __eq__ method for equality and inequality."""
        card1 = Card(Card.Suit.CLUBS, Card.Rank.FIVE)
        card2 = Card(Card.Suit.CLUBS, Card.Rank.FIVE)
        card3 = Card(Card.Suit.DIAMONDS, Card.Rank.FIVE)
        card4 = Card(Card.Suit.CLUBS, Card.Rank.SIX)
        joker1 = Card(None, Card.Rank.JOKER_RED)
        joker2 = Card(None, Card.Rank.JOKER_RED)

        self.assertEqual(card1, card2, "Identical cards should be equal.")
        self.assertNotEqual(card1, card3, "Cards with different suits should not be equal.")
        self.assertNotEqual(card1, card4, "Cards with different ranks should not be equal.")
        self.assertEqual(joker1, joker2, "Identical jokers should be equal.")
        self.assertNotEqual(card1, joker1, "A standard card should not be equal to a Joker.")
        self.assertNotEqual(card1, "5♣", "A card should not be equal to a string.")

    def test_card_value(self):
        """Tests the value() method for all card types."""
        self.assertEqual(Card(Card.Suit.HEARTS, Card.Rank.SEVEN).value(), 7)
        self.assertEqual(Card(Card.Suit.HEARTS, Card.Rank.ACE).value(), 1)
        self.assertEqual(Card(Card.Suit.HEARTS, Card.Rank.KING).value(), 10)
        self.assertEqual(Card(Card.Suit.HEARTS, Card.Rank.QUEEN).value(), 10)
        self.assertEqual(Card(Card.Suit.HEARTS, Card.Rank.JACK).value(), 10)
        self.assertEqual(Card(None, Card.Rank.JOKER_RED).value(), 0)

    def test_card_effects(self):
        """Tests that the correct effect is assigned based on rank and suit."""
        # King effects
        king_h = Card(Card.Suit.HEARTS, Card.Rank.KING)
        self.assertEqual(king_h.effect, Card.Effect.SHUFFLE, "Red Kings should have SHUFFLE effect.")
        king_d = Card(Card.Suit.DIAMONDS, Card.Rank.KING)
        self.assertEqual(king_d.effect, Card.Effect.SHUFFLE, "Red Kings should have SHUFFLE effect.")
        king_s = Card(Card.Suit.SPADES, Card.Rank.KING)
        self.assertEqual(king_s.effect, Card.Effect.DRAW, "Black Kings should have DRAW effect.")
        king_c = Card(Card.Suit.CLUBS, Card.Rank.KING)
        self.assertEqual(king_c.effect, Card.Effect.DRAW, "Black Kings should have DRAW effect.")

        # Queen and Jack effects
        queen = Card(Card.Suit.SPADES, Card.Rank.QUEEN)
        self.assertEqual(queen.effect, Card.Effect.SWAP, "Queens should have SWAP effect.")
        jack = Card(Card.Suit.SPADES, Card.Rank.JACK)
        self.assertEqual(jack.effect, Card.Effect.PEEK, "Jacks should have PEEK effect.")

        # No effect
        seven = Card(Card.Suit.SPADES, Card.Rank.SEVEN)
        self.assertEqual(seven.effect, Card.Effect.NONE, "Numeric cards should have no effect.")


if __name__ == '__main__':
    # This allows the script to be run directly from the command line
    unittest.main()
