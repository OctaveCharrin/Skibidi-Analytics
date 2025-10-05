from enum import Enum


class Card:
    class Suit(str, Enum):
        SPADES = "♠"
        HEARTS = "♥"
        DIAMONDS = "♦"
        CLUBS = "♣"

    class Rank(str, Enum):
        ACE = "A"
        TWO = "2"
        THREE = "3"
        FOUR = "4"
        FIVE = "5"
        SIX = "6"
        SEVEN = "7"
        EIGHT = "8"
        NINE = "9"
        TEN = "10"
        JACK = "J"
        QUEEN = "Q"
        KING = "K"
        JOKER_RED = "JOKER_RED"
        JOKER_BLACK = "JOKER_BLACK"

    class Effect(Enum):
        NONE = None
        SHUFFLE = "shuffle"
        DRAW = "draw"
        SWAP = "swap"
        PEEK = "peek"

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.effect = self._init_effect(suit, rank)

    def __repr__(self):
        if self.rank in [Card.Rank.JOKER_RED, Card.Rank.JOKER_BLACK]:
            return "★Black Joker★" if self.rank == Card.Rank.JOKER_BLACK else "★Red Joker★"
        return f"{self.rank.value}{self.suit.value}"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False

    @staticmethod
    def _init_effect(suit, rank):
        if rank == Card.Rank.KING:
            effect = (
                Card.Effect.SHUFFLE
                if suit in [Card.Suit.HEARTS, Card.Suit.DIAMONDS]
                else Card.Effect.DRAW
            )
        elif rank == Card.Rank.QUEEN:
            effect = Card.Effect.SWAP
        elif rank == Card.Rank.JACK:
            effect = Card.Effect.PEEK
        else:
            effect = Card.Effect.NONE
        return effect

    def value(self):
        if self.rank in [Card.Rank.JOKER_RED, Card.Rank.JOKER_BLACK]:
            return 0
        elif self.rank in [Card.Rank.JACK, Card.Rank.QUEEN, Card.Rank.KING]:
            return 10
        elif self.rank == Card.Rank.ACE:
            return 1
        else:
            return int(self.rank)
