import random
from typing import Any

from skibidi.card import Card
from skibidi.dealer import Dealer
from skibidi.game import Game
from skibidi.player import Player
from skibidi.strategy import Strategy


class RandomStrategy(Strategy):
    def select_draw_pile(public: Game.View, private: Player.View) -> Dealer.Source:
        return random.choice([Dealer.Source.DRAW, Dealer.Source.DISCARD])

    def select_card_to_exchange(
        public: Game.View, private: Player.View, source: Dealer.Source
    ) -> int:
        return random.randint(0, len(private.hand) - 1)

    def select_card_to_discard(public: Game.View, private: Player.View) -> int:
        card_to_discard = (
            public.dealer_view.discard_pile[-1]
            if public.dealer_view.discard_pile
            else None
        )
        if card_to_discard and card_to_discard in private.hand:
            return private.hand.index(card_to_discard) if random.random() < 0.7 else -1
        return -1

    def decide_effect(
        public: Game.View, private: Player.View, effect: Card.Effect
    ) -> Any:
        """Decide how to handle a card effect."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    def decide_call(public: Game.View, private: Player.View) -> int:
        call = random.choice([True, False], p=[0.1, 0.9])
        if call:
            return random.randint(0, len(private.hand) - 1)
        return -1
