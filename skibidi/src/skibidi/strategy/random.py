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
        if effect == Card.Effect.SHUFFLE or effect == Card.Effect.DRAW:
            return random.choice([name for name in private.opponents_hands.keys()])
        elif effect == Card.Effect.PEEK:
            return (private.name, random.randint(0, len(private.hand) - 1))
        elif effect == Card.Effect.SWAP:
            target1 = random.choice(
                [name for name in private.opponents_hands.keys()] + [private.name]
            )
            target2 = random.choice(
                [name for name in private.opponents_hands.keys()] + [private.name]
            )
            idx1 = random.randint(0, len(private.opponents_hands[target1]) - 1)
            idx2 = random.randint(0, len(private.opponents_hands[target2]) - 1)
            return (target1, idx1, target2, idx2)
        elif effect == Card.Effect.NONE:
            return None
        else:
            raise ValueError(f"Unknown effect: {effect}")

    def decide_call(public: Game.View, private: Player.View) -> int:
        # 10% chance to call
        call = random.random() < 0.1
        if call:
            return random.randint(0, len(private.hand) - 1)
        return -1
