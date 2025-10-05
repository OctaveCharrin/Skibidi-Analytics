import random
from enum import Enum

from skibidi.card import Card


class Dealer:

    class Source(Enum):
        DRAW = 0
        DISCARD = 1

        def __str__(self):
            return "Draw Pile" if self == Dealer.Source.DRAW else "Discard Pile"

    class View:
        def __init__(self, dealer: "Dealer"):
            self.draw_pile_size = len(dealer.draw_pile)
            self.discard_pile = dealer.discard_pile

        def update(self, dealer: "Dealer"):
            self.draw_pile_size = len(dealer.draw_pile)
            self.discard_pile = dealer.discard_pile

        def __repr__(self, indent: str = "") -> str:
            """Provides a clean, indented representation of the dealer's view."""

            # Helper to format the discard pile for readability
            discard_str = f"[{', '.join(str(c) for c in self.discard_pile)}]"

            return (
                f"Dealer.View(\n"
                f"{indent}   (draw_pile_size): {self.draw_pile_size}\n"
                f"{indent}   (discard_pile): {discard_str}\n"
                f"{indent}   )"
            )

    def __init__(self, hand_size: int = 5, treasure_size: int = 3):
        self.hand_size = hand_size
        self.treasure_size = treasure_size
        self.deck = self.init_deck()
        self.draw_pile: list[Card] = self.deck[:]
        self.discard_pile: list[Card] = []
        self.treasure: list[Card] = []
        self.view = Dealer.View(self)

    def init_deck(self):
        deck = [
            Card(suit, rank)
            for suit in Card.Suit
            for rank in Card.Rank
            if rank not in [Card.Rank.JOKER_RED, Card.Rank.JOKER_BLACK]
        ]
        deck += [Card(None, Card.Rank.JOKER_RED), Card(None, Card.Rank.JOKER_BLACK)]
        return deck

    def reset_deck(self):
        self.draw_pile = self.deck[:]
        random.shuffle(self.draw_pile)
        self.discard_pile = []
        self.treasure = []
        self.view.update(self)

    def reshuffle_discard_into_draw(self):
        discard_top = self.discard_pile.pop() if self.discard_pile else None
        self.draw_pile = self.discard_pile[:]
        random.shuffle(self.draw_pile)
        self.discard_pile = [] if discard_top is None else [discard_top]

    def deal_initial_hands(self, hands: dict[str, list[Card]]):
        if len(self.draw_pile) < (len(hands) * self.hand_size + self.treasure_size + 1):
            raise ValueError("Not enough cards to deal initial hands and treasure.")
        # Deal hands
        for _ in range(self.hand_size):
            for player in hands.keys():
                card = self.draw_pile.pop()
                hands[player].append(card)
        # Deal treasure
        for _ in range(self.treasure_size):
            card = self.draw_pile.pop()
            self.treasure.append(card)
        # Start discard pile
        card = self.draw_pile.pop()
        self.discard_pile.append(card)
        self.view.update(self)

    def draw_from_draw(self):
        if not self.draw_pile:
            self.reshuffle_discard_into_draw()
        if self.draw_pile:
            card = self.draw_pile.pop()
            self.view.update(self)
            return card
        raise ValueError("Deck is empty.")

    def draw_from_discard(self):
        if self.discard_pile:
            card = self.discard_pile.pop()
            self.view.update(self)
            return card
        raise ValueError("Discard pile is empty.")

    def draw(self, source: "Dealer.Source"):
        if source == Dealer.Source.DRAW:
            return self.draw_from_draw()
        elif source == Dealer.Source.DISCARD:
            return self.draw_from_discard()
        raise ValueError("Invalid source specified.")

    def discard(self, card: Card):
        self.discard_pile.append(card)
        self.view.update(self)
