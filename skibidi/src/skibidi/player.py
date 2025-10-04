# player.py

from skibidi.card import Card
from skibidi.game import Game
from skibidi.strategy import Strategy


class Player:

    class View:
        def __init__(self, game: Game, player: "Player"):
            self.drawn_card: Card | None = None
            self.hand: list[Card | None] = [None] * game.dealer.hand_size
            self.opponents_hands: dict[str, list[Card | None]] = {
                p.name: [None] * game.dealer.hand_size
                for p in game.players
                if p != player
            }
            self.treasure: list[Card | None] = [None] * game.dealer.treasure_size

        def reset(self, game: Game, player: "Player"):
            self.drawn_card: Card | None = None
            self.hand: list[Card | None] = [None] * game.dealer.hand_size
            self.opponents_hands: dict[str, list[Card | None]] = {
                p.name: [None] * game.dealer.hand_size
                for p in game.players
                if p != player
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
                f"{indent})"
            )

    def __init__(self, game: "Game", name: str, strategy: Strategy = None) -> None:
        self.name = name
        self.strategy = strategy
        self.view: Player.View = Player.View(game, self)

    def learn_card(self, idx: int, card: Card) -> None:
        if 0 <= idx < len(self.view.hand):
            self.view.hand[idx] = card
        else:
            raise ValueError("Invalid card index.")

    def learn_opponent_card(self, opponent: "Player", idx: int, card: Card) -> None:
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
        view_repr = self.view.__repr__(indent=indent + "  ")
        return (
            f"Player(\n"
            f"{indent}    (name): {self.name}\n"
            f"{indent}    (strategy): {strategy_name}\n"
            f"{indent}    (view): {view_repr}\n"
            f"{indent})"
        )
