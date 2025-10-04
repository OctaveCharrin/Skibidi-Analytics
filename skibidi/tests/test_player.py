import unittest
from unittest.mock import MagicMock

from skibidi.card import Card
from skibidi.game import Game
from skibidi.player import Player
from skibidi.strategy import Strategy


class TestPlayer(unittest.TestCase):
    """Unit test suite for the Player class and its nested View."""

    def setUp(self):
        """Set up mock objects and a Player instance for each test."""
        # Mock the Strategy class
        self.mock_strategy = MagicMock(spec=Strategy)

        # Mock the Game object and its nested attributes
        self.mock_game = MagicMock(spec=Game)
        # Ensure the mock_game has a dealer attribute (spec=Game doesn't create instance attrs)
        self.mock_game.dealer = MagicMock()

        # Mock players needed for the game context
        self.player1_mock_for_game = MagicMock(spec=Player)
        self.player1_mock_for_game.name = "P1"
        self.player2_mock_for_game = MagicMock(spec=Player)
        self.player2_mock_for_game.name = "P2"

        # Configure the mock_game's players list
        self.mock_game.players = [
            self.player1_mock_for_game,
            self.player2_mock_for_game,
        ]

        # Configure the mock_game's dealer attributes
        self.mock_game.dealer.hand_size = 5
        self.mock_game.dealer.treasure_size = 3

        # Create the Player instance that we will be testing
        self.player = Player(self.mock_game, name="P1", strategy=self.mock_strategy)
        # Player no longer initializes its view in __init__; initialize it now
        self.player.init_view(self.mock_game)

    def test_player_initialization(self):
        """Test that the Player and its View are initialized correctly."""
        self.assertEqual(self.player.name, "P1")
        self.assertIs(self.player.strategy, self.mock_strategy)
        self.assertIsInstance(self.player.view, Player.View)

    def test_view_initialization(self):
        """Test the initial state of the Player.View."""
        view = self.player.view
        self.assertIsNone(view.drawn_card)
        self.assertEqual(len(view.hand), self.mock_game.dealer.hand_size)
        self.assertEqual(view.hand, [None] * self.mock_game.dealer.hand_size)

        # The view should contain opponents, but not the player themselves
        self.assertIn("P2", view.opponents_hands)
        self.assertNotIn("P1", view.opponents_hands)
        self.assertEqual(
            len(view.opponents_hands["P2"]), self.mock_game.dealer.hand_size
        )

        self.assertEqual(len(view.treasure), self.mock_game.dealer.treasure_size)

    def test_learn_card(self):
        """Test learning a card in the player's own hand."""
        card = Card(Card.Suit.SPADES, Card.Rank.ACE)
        self.player.learn_card(2, card)
        self.assertIs(self.player.view.hand[2], card)

    def test_learn_card_invalid_index(self):
        """Test that learning a card with an invalid index raises a ValueError."""
        card = Card(Card.Suit.SPADES, Card.Rank.ACE)
        with self.assertRaises(ValueError):
            self.player.learn_card(99, card)  # Index out of bounds

    def test_learn_opponent_card(self):
        """Test learning a card in an opponent's hand."""
        card = Card(Card.Suit.HEARTS, Card.Rank.KING)
        opponent = self.player2_mock_for_game  # The mock opponent from setUp

        self.player.learn_opponent_card(opponent, 3, card)

        self.assertIs(self.player.view.opponents_hands["P2"][3], card)

    def test_learn_opponent_card_invalid_opponent(self):
        """Test learning a card for an opponent not in the game."""
        card = Card(Card.Suit.HEARTS, Card.Rank.KING)
        # Create a mock for an opponent that was not in the initial game.players list
        unknown_opponent = MagicMock(spec=Player)
        unknown_opponent.name = "P99"

        with self.assertRaises(ValueError):
            self.player.learn_opponent_card(unknown_opponent, 0, card)

    def test_learn_opponent_card_invalid_index(self):
        """Test learning an opponent's card with an invalid index."""
        card = Card(Card.Suit.HEARTS, Card.Rank.KING)
        opponent = self.player2_mock_for_game

        with self.assertRaises(ValueError):
            self.player.learn_opponent_card(opponent, 99, card)

    def test_view_reset(self):
        """Test that the view's reset method clears all learned information."""
        # Modify the view state
        self.player.view.drawn_card = Card(Card.Suit.CLUBS, Card.Rank.TWO)
        self.player.learn_card(0, Card(Card.Suit.CLUBS, Card.Rank.THREE))
        self.player.learn_opponent_card(
            self.player2_mock_for_game, 1, Card(Card.Suit.CLUBS, Card.Rank.FOUR)
        )

        # Reset the view
        self.player.view.reset(self.mock_game, self.player)

        # Check that the state is back to its initial empty state
        self.assertIsNone(self.player.view.drawn_card)
        self.assertEqual(
            self.player.view.hand, [None] * self.mock_game.dealer.hand_size
        )
        self.assertEqual(
            self.player.view.opponents_hands["P2"],
            [None] * self.mock_game.dealer.hand_size,
        )

    def test_repr_methods(self):
        """Test the string representations of Player and Player.View."""
        player_repr = repr(self.player)
        view_repr = repr(self.player.view)

        # Test Player repr
        self.assertIn("Player(", player_repr)
        self.assertIn("(name): P1", player_repr)
        self.assertIn(
            f"(strategy): {self.mock_strategy.__class__.__name__}", player_repr
        )
        self.assertIn("(view): Player.View(", player_repr)

        # Test View repr
        self.assertIn("Player.View(", view_repr)
        self.assertIn("(drawn_card): None", view_repr)
        self.assertIn("(hand): [?, ?, ?, ?, ?]", view_repr)
        self.assertIn("(opponents_hands):", view_repr)
        self.assertIn("'P2': [?, ?, ?, ?, ?]", view_repr)


if __name__ == "__main__":
    unittest.main()
