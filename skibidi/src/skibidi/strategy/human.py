from typing import TYPE_CHECKING, Any, Optional

from skibidi.card import Card
from skibidi.dealer import Dealer
from skibidi.strategy.strategy import Strategy

if TYPE_CHECKING:
    from skibidi.game import Game
    from skibidi.player import Player


def _print_view(label: str, view: object) -> None:
    """Safe print helper for views."""
    print(f"=== {label} ===")
    # Assume views provide a helpful __repr__ per README; print it.
    try:
        print(view)
    except Exception:
        # Fallback: print selected known attributes if repr fails
        attrs = [
            "dealer_view",
            "drawn_card",
            "hand",
            "opponents_hands",
            "treasure",
            "effects_queue",
            "scores",
            "round",
        ]
        for a in attrs:
            if hasattr(view, a):
                try:
                    print(f"{a}: {getattr(view, a)}")
                except Exception:
                    print(f"{a}: <unprintable>")
    print("=" * 20)


def _choose_int(prompt: str, minv: int, maxv: int, allow_negative_one: bool = True) -> int:
    """Prompt until a valid integer in [minv, maxv] (or -1 if allowed) is entered."""
    while True:
        val = input(f"{prompt} (enter integer between {minv} and {maxv}"
                    + (", or -1" if allow_negative_one else "") + "): ").strip()
        if allow_negative_one and val == "-1":
            return -1
        try:
            i = int(val)
        except ValueError:
            print("Not an integer, try again.")
            continue
        if i < minv or i > maxv:
            print("Out of range, try again.")
            continue
        return i


def _choose_player_name(prompt: str, candidates: Optional[list[str]]) -> Optional[str]:
    """Prompt user to choose a player name from candidates or none (empty)."""
    if candidates:
        print(f"Available players: {', '.join(candidates)}")
    while True:
        val = input(f"{prompt} (enter player name or empty for 'None'): ").strip()
        if val == "":
            return None
        # If no candidates provided, accept any non-empty name
        if candidates is None:
            return val

        if val in candidates:
            return val

        # Offer to accept a free-text name if the user really wants it
        yn = input(f"'{val}' isn't in the known players. Accept this name anyway? (y/n): ").strip().lower()
        if yn in ("y", "yes"):
            return val
        print("Unknown player name, try again.")


class HumanStrategy(Strategy):
    """Interactive strategy that asks the human operator on stdin for each decision.

    Notes:
    - Methods are static to match the Strategy API: they receive public and private views.
    - The functions validate basic input and will re-prompt until a legal value is provided.
    """

    @staticmethod
    def select_draw_pile(public: "Game.View", private: "Player.View") -> Dealer.Source:
        # Print concise public/private info per README structure
        _print_view("Public view", public)
        _print_view("Your private view", private)
        while True:
            choice = input("Choose draw pile - (D)RAW or (X)DISCARD: ").strip().lower()
            if choice in ("d", "draw"):
                return Dealer.Source.DRAW
            if choice in ("x", "discard", "dsc"):
                return Dealer.Source.DISCARD
            print("Invalid choice, please enter 'draw' or 'discard' (or D/X).")

    @staticmethod
    def select_card_to_exchange(
        public: "Game.View", private: "Player.View", source: Dealer.Source
    ) -> int:
        _print_view("Public view", public)
        _print_view("Your private view", private)
        # private.hand is documented in README as list[Card|None]
        hand_len = len(getattr(private, "hand", []))
        if hand_len == 0:
            print("No cards in hand to exchange; will discard drawn card (-1).")
            return -1
        return _choose_int(
            "Select index of card to exchange (or -1 to discard the drawn card)",
            0,
            hand_len - 1,
            allow_negative_one=True,
        )

    @staticmethod
    def select_card_to_discard(public: "Game.View", private: "Player.View") -> int:
        _print_view("Public view", public)
        _print_view("Your private view", private)
        hand_len = len(getattr(private, "hand", []))
        if hand_len == 0:
            print("No cards in hand to discard; returning -1.")
            return -1
        return _choose_int(
            "Select index of card to discard (or -1 for no discard)",
            0,
            hand_len - 1,
            allow_negative_one=True,
        )

    @staticmethod
    def decide_effect(public: "Game.View", private: "Player.View", effect: Card.Effect) -> Any:
        # Print views
        _print_view("Public view", public)
        _print_view("Your private view", private)

        # Derive candidate player names from private.opponents_hands per README
        candidates = None
        if hasattr(private, "opponents_hands") and isinstance(private.opponents_hands, dict):
            try:
                candidates = list(private.opponents_hands.keys())
            except Exception:
                candidates = None

        # Also include any player names that may be present in public.effects_queue
        if candidates is None:
            candidates = []
        if hasattr(public, "effects_queue") and public.effects_queue:
            try:
                for p, _ in public.effects_queue:
                    name = getattr(p, "name", None)
                    if name and name not in candidates:
                        candidates.append(name)
            except Exception:
                # ignore if effects_queue doesn't contain Player objects
                pass
        if not candidates:
            candidates = None

        if effect in (Card.Effect.DRAW, Card.Effect.SHUFFLE):
            # Ask for target player or none
            name = _choose_player_name(
                f"Effect {effect.name}: choose target player to apply effect to", candidates
            )
            return name  # can be None

        if effect is Card.Effect.PEEK:
            # ask for player and index
            target = _choose_player_name("Choose player to peek at", candidates)
            if target is None:
                print("Peek cancelled.")
                return None
            # try to get opponent hand length if available on public
            opponent_hand_len = None
            # Prefer private.opponents_hands info (known by this player)
            if hasattr(private, "opponents_hands") and isinstance(private.opponents_hands, dict):
                opponent_hand = private.opponents_hands.get(target)
                if opponent_hand is not None:
                    opponent_hand_len = len(opponent_hand)

            # Fallback to public.hands (if present) or to player's own hand length
            if opponent_hand_len is None and hasattr(public, "hands") and isinstance(public.hands, dict):
                opponent_hand_len = len(public.hands.get(target, []))

            hand_len = opponent_hand_len if opponent_hand_len is not None else max(0, len(getattr(private, "hand", [])))
            if hand_len == 0:
                print("No known card positions for that opponent; returning None.")
                return None
            idx = _choose_int(f"Index of card to peek in {target}'s hand", 0, hand_len - 1, allow_negative_one=False)
            return (target, idx)

        if effect is Card.Effect.SWAP:
            # ask for two players and two indices
            p1 = _choose_player_name("First player to swap (player1)", candidates)
            if p1 is None:
                print("Swap cancelled.")
                return None
            p2 = _choose_player_name("Second player to swap (player2)", candidates)
            if p2 is None:
                print("Swap cancelled.")
                return None
            # best-effort to get lengths
            def _hand_len_for(name: str) -> int:
                # Prefer private.opponents_hands when available
                if hasattr(private, "opponents_hands") and isinstance(private.opponents_hands, dict):
                    h = private.opponents_hands.get(name)
                    if h is not None:
                        return len(h)
                if hasattr(public, "hands") and isinstance(public.hands, dict):
                    return len(public.hands.get(name, []))
                return len(getattr(private, "hand", []))

            l1 = _hand_len_for(p1)
            l2 = _hand_len_for(p2)
            if l1 == 0 or l2 == 0:
                print("One of the players has no known hand size; cancelling swap.")
                return None
            i1 = _choose_int(f"Index in {p1}'s hand to swap", 0, l1 - 1, allow_negative_one=False)
            i2 = _choose_int(f"Index in {p2}'s hand to swap", 0, l2 - 1, allow_negative_one=False)
            return (p1, i1, p2, i2)

        # NONE or unrecognized effects: return None
        return None

    @staticmethod
    def decide_call(public: "Game.View", private: "Player.View") -> int:
        _print_view("Public view", public)
        _print_view("Your private view", private)
        hand_len = len(getattr(private, "hand", []))
        if hand_len <= 1:
            # For one-card hand, ask yes/no; if yes return 0 (per convention)
            while True:
                ans = input("Do you want to call the round end? (y/n): ").strip().lower()
                if ans in ("y", "yes"):
                    return 0
                if ans in ("n", "no"):
                    return -1
                print("Please answer y or n.")
        # For larger hands ask for index or -1
        return _choose_int("Select index to call (or -1 for no call)", 0, max(0, hand_len - 1), allow_negative_one=True)