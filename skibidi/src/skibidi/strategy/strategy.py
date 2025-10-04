from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from skibidi.game import Game
    from skibidi.dealer import Dealer
    from skibidi.player import Player
    from skibidi.card import Card


# Abstract base class for strategies
class Strategy:
    @staticmethod
    def select_draw_pile(public: "Game.View", private: "Player.View") -> "Dealer.Source":
        """Select from which pile to draw a card.

        Args:
            public (Game.View): The public view of the game.
            private (Player.View): The player's private view of the game.

        Returns:
            Dealer.Source: The selected draw pile source.
            Should be either Dealer.Source.DRAW or Dealer.Source.DISCARD.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @staticmethod
    def select_card_to_exchange(
        public: "Game.View", private: "Player.View", source: "Dealer.Source"
    ) -> int:
        """Select which card to exchange from hand.

        Args:
            public (Game.View): The public view of the game.
            private (Player.View): The player's private view of the game.
            source (Dealer.Source): The source from which the card was drawn.

        Returns:
            int: The index of the card to exchange, or -1 to discard the drawn card.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @staticmethod
    def select_card_to_discard(public: "Game.View", private: "Player.View") -> int:
        """Select which card to discard from hand.

        Args:
            public (Game.View): The public view of the game.
            private (Player.View): The player's private view of the game.

        Returns:
            int: The index of the card to discard, or -1 for no discard.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @staticmethod
    def decide_effect(
        public: "Game.View", private: "Player.View", effect: "Card.Effect"
    ) -> Any:
        """Decide how to handle a card effect.

        Args:
            public (Game.View): The public view of the game.
            private (Player.View): The player's private view of the game.
            effect (Card.Effect): The card effect to handle.

        Returns:
            Any: The decision made regarding the card effect.

        ***Conventions***:
            - For `Card.Effect.DRAW` or `Card.Effect.SHUFFLE`: return the name of the target player as a **string**.
            - For `Card.Effect.SWAP`: return a tuple **(player1: str, index1: int, player2: str, index2: int)**.
                This indicates that *player1's* card at *index1* should be swapped with *player2's* card at *index2*.
            - For `Card.Effect.PEEK`: return a tuple **(target_player_name: str, card_index: int)**.
                This indicates that the player wants to peek at the card at *card_index* in *target_player_name*'s hand.
            - *Optional*: For `Card.Effect.NONE`: return None.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @staticmethod
    def decide_call(public: "Game.View", private: "Player.View") -> int:
        """Decide whether to call the end of the round.

        Args:
            public (Game.View): The public view of the game.
            private (Player.View): The player's private view of the game.

        Returns:
            int: The index of the card to discard, or -1 for no call.

        **Note**: If only one card is in hand, call with some positive index (e.g. 0), even though this card will not be discarded.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
