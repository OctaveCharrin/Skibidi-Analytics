import importlib
import inspect
import pkgutil
import unittest

from skibidi.card import Card
from skibidi.dealer import Dealer
from skibidi.strategy.strategy import Strategy


# Minimal fake views used to call strategy methods
class _FakeDealerView:
    def __init__(self):
        self.discard_pile = []
        self.draw_pile = [Card(Card.Suit.HEARTS, Card.Rank.ACE)]


class _FakePublicView:
    def __init__(self):
        self.dealer_view = _FakeDealerView()
        # players names used by strategies that may return player-name strings
        self.player_names = ["P1", "P2"]


class _FakePrivateView:
    def __init__(self, hand, name: str = "P1"):
        self.hand = hand
        # name of the player owning this view (some strategies reference it)
        self.name = name
        # mapping of opponent name -> list of known cards (None = unknown)
        # Include the player's own name with a same-length list to support
        # strategies that may reference private.name and then index into
        # private.opponents_hands[private.name]. This mirrors the minimal
        # information a player's view might provide.
        self.opponents_hands = {"P2": [None] * len(hand), self.name: [None] * len(hand)}


class TestStrategyImplementations(unittest.TestCase):
    """Discover strategy implementations and validate their API / return conventions."""

    def test_all_strategies_conform(self):
        # import the package and iterate modules
        pkg = importlib.import_module("skibidi.strategy")
        package_path = pkg.__path__  # type: ignore

        # create sample views for calls
        sample_hand = [
            Card(Card.Suit.CLUBS, Card.Rank.TWO),
            Card(Card.Suit.SPADES, Card.Rank.THREE),
        ]
        public = _FakePublicView()
        private = _FakePrivateView(sample_hand)

        # iterate all modules inside skibidi.strategy package
        for finder, name, ispkg in pkgutil.iter_modules(package_path):
            # Skip package internals and the abstract base module
            if name == "strategy" or name.startswith("__"):
                continue
            # Exclude the interactive human strategy from automated checks
            if name == "human":
                continue
            module_name = f"skibidi.strategy.{name}"
            module = importlib.import_module(module_name)

            # find all Strategy subclasses in module
            for _, cls in inspect.getmembers(module, inspect.isclass):
                # Skip the interactive HumanStrategy class (requires stdin)
                if cls.__name__ == "HumanStrategy":
                    continue
                if not issubclass(cls, Strategy) or cls is Strategy:
                    continue

                with self.subTest(strategy=cls.__name__):
                    # ensure required callables are present
                    for method in (
                        "select_draw_pile",
                        "select_card_to_exchange",
                        "select_card_to_discard",
                        "decide_effect",
                        "decide_call",
                    ):
                        self.assertTrue(
                            hasattr(cls, method),
                            msg=f"{cls.__name__} missing required method: {method}",
                        )

                    # Call select_draw_pile and expect a Dealer.Source enum
                    try:
                        src = getattr(cls, "select_draw_pile")(public, private)
                    except NotImplementedError:
                        self.fail(f"{cls.__name__}.select_draw_pile not implemented")
                    self.assertIn(
                        src,
                        (Dealer.Source.DRAW, Dealer.Source.DISCARD),
                        msg=f"{cls.__name__}.select_draw_pile returned invalid value: {src}",
                    )

                    # Call select_card_to_exchange -> int in [-1, len(hand)-1]
                    try:
                        idx = getattr(cls, "select_card_to_exchange")(
                            public, private, Dealer.Source.DRAW
                        )
                    except NotImplementedError:
                        self.fail(
                            f"{cls.__name__}.select_card_to_exchange not implemented"
                        )
                    self.assertIsInstance(idx, int)
                    self.assertGreaterEqual(
                        idx, -1, msg=f"{cls.__name__}.select_card_to_exchange < -1"
                    )
                    self.assertLessEqual(
                        idx,
                        len(private.hand) - 1,
                        msg=f"{cls.__name__}.select_card_to_exchange >= hand size",
                    )

                    # Call select_card_to_discard -> int in [-1, len(hand)-1]
                    try:
                        didx = getattr(cls, "select_card_to_discard")(public, private)
                    except NotImplementedError:
                        self.fail(
                            f"{cls.__name__}.select_card_to_discard not implemented"
                        )
                    self.assertIsInstance(didx, int)
                    self.assertGreaterEqual(
                        didx, -1, msg=f"{cls.__name__}.select_card_to_discard < -1"
                    )
                    self.assertLessEqual(
                        didx,
                        len(private.hand) - 1,
                        msg=f"{cls.__name__}.select_card_to_discard >= hand size",
                    )

                    # decide_effect: exercise each Card.Effect and validate return type follows conventions
                    for effect in Card.Effect:
                        try:
                            res = getattr(cls, "decide_effect")(public, private, effect)
                        except NotImplementedError:
                            self.fail(f"{cls.__name__}.decide_effect not implemented")
                        # For DRAW/SHUFFLE expect either None or a player-name string
                        if effect in (Card.Effect.DRAW, Card.Effect.SHUFFLE):
                            self.assertTrue(
                                res is None or isinstance(res, str),
                                msg=f"{cls.__name__}.decide_effect({effect}) should return a player-name str or None, got {res}",
                            )
                        elif effect is Card.Effect.SWAP:
                            # expect tuple (str,int,str,int)
                            self.assertTrue(
                                isinstance(res, tuple)
                                and len(res) == 4
                                and isinstance(res[0], str)
                                and isinstance(res[1], int)
                                and isinstance(res[2], str)
                                and isinstance(res[3], int),
                                msg=f"{cls.__name__}.decide_effect(SWAP) should return (str,int,str,int), got {res}",
                            )
                        elif effect is Card.Effect.PEEK:
                            self.assertTrue(
                                isinstance(res, tuple)
                                and len(res) == 2
                                and isinstance(res[0], str)
                                and isinstance(res[1], int),
                                msg=f"{cls.__name__}.decide_effect(PEEK) should return (str,int), got {res}",
                            )
                        else:
                            # NONE or other effects: allow None or sensible types
                            self.assertTrue(
                                res is None or isinstance(res, (str, tuple, int)),
                                msg=f"{cls.__name__}.decide_effect({effect}) returned unexpected type: {type(res)}",
                            )

                    # decide_call -> int in [-1, len(hand)-1]
                    try:
                        call_idx = getattr(cls, "decide_call")(public, private)
                    except NotImplementedError:
                        self.fail(f"{cls.__name__}.decide_call not implemented")
                    self.assertIsInstance(call_idx, int)
                    self.assertGreaterEqual(call_idx, -1)
                    self.assertLessEqual(call_idx, len(private.hand) - 1)


if __name__ == "__main__":
    unittest.main()
