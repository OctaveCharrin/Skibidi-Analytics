from typing import TYPE_CHECKING

from skibidi.card import Card
from skibidi.strategy import Strategy

if TYPE_CHECKING:
    from skibidi.game import Game


class Player:
    """
    Player model and its nested View.

    Initialization note (important):
    - The Game is responsible for constructing Player instances but does NOT
      rely on Player creating its View during Player.__init__.
    - This avoids an initialization ordering problem where Player.View's
      constructor needs to inspect `game.players` while the Game is still
      constructing that list. Instead the Game should:
        1. create all Player(...) objects (they will have view == None),
        2. create any per-player hand structures (e.g. game.hands),
        3. call player.init_view(game) for each player so Player.View can
           safely read `game.players` and dealer sizes, and
        4. finally create higher-level views like Game.View that depend on
           the completed players list.

    This ordering keeps construction safe and predictable and is relied on by
    unit tests which may create Players with a mock Game and then call
    init_view(...) explicitly.
    """

    class View:
        def __init__(self, game: "Game", player: "Player"):
            self.drawn_card: Card | None = None
            self.hand: list[Card | None] = [None] * game.dealer.hand_size
            # Use name comparison as they should be unique and so that
            # tests that use mock Player objects work
            self.opponents_hands: dict[str, list[Card | None]] = {
                p.name: [None] * game.dealer.hand_size
                for p in game.players
                if p.name != player.name
            }
            self.treasure: list[Card | None] = [None] * game.dealer.treasure_size

        def reset(self, game: "Game", player: "Player"):
            self.drawn_card: Card | None = None
            self.hand: list[Card | None] = [None] * game.dealer.hand_size
            self.opponents_hands: dict[str, list[Card | None]] = {
                p.name: [None] * game.dealer.hand_size
                for p in game.players
                if p.name != player.name
            }
            self.treasure: list[Card | None] = [None] * game.dealer.treasure_size

        def __repr__(self, indent: str = "") -> str:

            def format_cards(cards: list[Card | None]) -> str:
                return f"[{', '.join(str(c) if c else '?' for c in cards)}]"

            opponents_str = "{\n"
            for name, hand in self.opponents_hands.items():
                opponents_str += f"{indent}        '{name}': {format_cards(hand)},\n"
            if self.opponents_hands:
                opponents_str = opponents_str.rstrip(",\n") + f"\n{indent}    }}"
            else:
                opponents_str = "{}"

            return (
                f"Player.View(\n"
                f"{indent}    (drawn_card): {self.drawn_card or 'None'}\n"
                f"{indent}    (hand): {format_cards(self.hand)}\n"
                f"{indent}    (opponents_hands): {opponents_str}\n"
                f"{indent}    (treasure): {format_cards(self.treasure)}\n"
                f")"
            )

    def __init__(self, game: "Game", name: str, strategy: Strategy = None) -> None:
        self.name = name  # Player's name, serves as unique identifier
        self.strategy = strategy
        # Do not initialize the view here; Game initializes views after
        # creating all Player instances to avoid ordering problems.
        self.view: Player.View | None = None

    def __eq__(self, value):
        if not isinstance(value, Player):
            return False
        return self.name == value.name

    def init_view(self, game: "Game"):
        self.view = Player.View(game, self)

    def learn_card(self, idx: int, card: Card) -> None:
        if not self.view:
            raise RuntimeError("Player view is not initialized. Call init_view(game) first.")
        if 0 <= idx < len(self.view.hand):
            self.view.hand[idx] = card
        else:
            raise ValueError("Invalid card index.")

    def learn_opponent_card(self, opponent: "Player", idx: int, card: Card) -> None:
        if not self.view:
            raise RuntimeError("Player view is not initialized. Call init_view(game) first.")
        if opponent.name in self.view.opponents_hands:
            if 0 <= idx < len(self.view.opponents_hands[opponent.name]):
                self.view.opponents_hands[opponent.name][idx] = card
            else:
                raise ValueError("Invalid card index.")
        else:
            raise ValueError("Opponent not found.")

    def __repr__(self, indent: str = "") -> str:
        """Provides a representation of the Player."""
        strategy_name = self.strategy.__class__.__name__ if self.strategy else "None"
        view_repr = self.view.__repr__(indent + "  ") if self.view else "None"
        return (
            f"Player(\n"
            f"{indent}    (name): {self.name}\n"
            f"{indent}    (strategy): {strategy_name}\n"
            f"{indent}    (view): {view_repr}\n"
            f"{indent})"
        )
