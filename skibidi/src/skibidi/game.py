import random
from typing import Any

from skibidi.card import Card
from skibidi.dealer import Dealer
from skibidi.player import Player


class Game:

    class View:
        def __init__(self, game: "Game"):
            self.dealer_view: Dealer.View = game.dealer.view
            self.effects_queue: list[tuple[Player, Card.Effect]] = []
            self.current_player_index: int = 0
            self.scores = [0] * len(game.players)
            self.round = 0

        def update(self, game: "Game"):
            self.dealer_view.update(game.dealer)
            self.current_player_index = game.current_player_index

        def __repr__(self, indent: str = "") -> str:

            effects_str = (
                f"[{', '.join(f'({p.name}, {e})' for p, e in self.effects_queue)}]"
            )
            dealer_view_repr = self.dealer_view.__repr__(indent=indent + "  ")

            return (
                f"Game.View(\n"
                f"{indent}    (round): {self.round}\n"
                f"{indent}    (scores): {self.scores}\n"
                f"{indent}    (effects_queue): {effects_str}\n"
                f"{indent}    (dealer): {dealer_view_repr}\n"
                f"{indent})"
            )

    def __init__(
        self,
        n_players: int = 5,
        names: list[str] = None,
        hand_size: int = 5,
        treasure_size: int = 3,
        initially_known: int = 2,
    ):
        self.dealer: Dealer = Dealer(self, hand_size, treasure_size)
        if names is None:
            self.players: list[Player] = [
                Player(f"Player {i + 1}") for i in range(n_players)
            ]
        else:
            self.players: list[Player] = [Player(name) for name in names]
        self.hands: dict[str, list[Card]] = {p.name: [] for p in self.players}
        self.current_player_index: int = 0
        self.caller_index: int = -1
        self.view: Game.View = Game.View(self)
        self.initially_known = initially_known

    def play(self):
        # Ensure all players have a strategy
        for player in self.players:
            if player.strategy is None:
                raise ValueError(f"Player {player.name} has no strategy assigned.")

        while not self.is_finished():
            self.init_round()
            while (
                self.caller_index < 0 or self.current_player_index != self.caller_index
            ):
                # Player turn
                current_player = self.players[self.current_player_index]

                # Choose draw source and draw card
                source = current_player.strategy.select_draw_pile(
                    self.view, current_player.view
                )
                card = self.dealer.draw(source)

                # Update player's view
                current_player.view.drawn_card = card

                # Decide which card to exchange
                exchange_index = current_player.strategy.select_card_to_exchange(
                    self.view, current_player.view, source
                )
                while exchange_index < 0 and source == Dealer.Source.DISCARD:
                    print("Invalid choice, cannot discard from discard pile.")
                    exchange_index = current_player.strategy.select_card_to_exchange(
                        self.view, current_player.view, source
                    )

                # Exchange or discard the card depending on the decision
                if exchange_index == -1:
                    self.discard(current_player, card=card)
                else:
                    old_card = self.exchange(current_player, exchange_index, card)
                    if source == Dealer.Source.DISCARD:
                        self.reveal_to_others(current_player, exchange_index, card)
                    self.discard(current_player, card=old_card)

                # Other players discard their cards
                self.allow_discards(current_player)

                # Applying effects of cards
                while self.view.effects_queue:
                    player, effect = self.view.effects_queue.pop(0)
                    decision = player.strategy.decide_effect(
                        self.view, player.view, effect
                    )
                    self.apply_effect(player, effect, decision)

                # Decide whether to call
                call_discard_index = current_player.strategy.decide_call(
                    self.view, current_player.view
                )
                if 0 <= call_discard_index < len(self.hands[current_player.name]):
                    print(f"Player {current_player.name} calls the end of the round!")
                    if len(self.hands[current_player.name]) > 1:
                        self.discard(current_player, idx=call_discard_index)
                        self.caller_index = self.current_player_index
                        # Other players discard their cards
                        self.allow_discards(current_player)
                    else:
                        print(
                            f"Discarding card ignored since only one card left in hand."
                        )
                else:
                    print("No call made.")

                self.current_player_index = (self.current_player_index + 1) % len(
                    self.players
                )
                self.view.update(self)
            # End of round
            self.end_round()
        # Game over
        self.end_game()

    def get_player_by_name(self, name: str) -> Player:
        for player in self.players:
            if player.name == name:
                return player
        raise ValueError(f"No player found with name {name}.")

    def discard(self, player: Player, card: Card = None, idx: int = None):
        if card is None and idx is None:
            raise ValueError("Either card or idx must be provided.")
        if card is not None:  # Discard the provided card
            player.view.drawn_card = None
        elif not (0 <= idx < len(self.hands[player.name])):
            raise ValueError("Invalid index for discard.")
        else:  # Discard the card at the provided index
            card = self.hands[player.name].pop(idx)
            # Update player's view
            player.view.hand.pop(idx)
            # Update opponents' views
            for opponent in self.players:
                if opponent != player:
                    opponent.view.opponents_hands[player.name].pop(idx)
        self.dealer.discard(card)
        if card.effect != Card.Effect.NONE:
            self.view.effects_queue.append((player, card.effect))

    def exchange(
        self, player: Player, idx: int, card: Card, reveal: bool = True
    ) -> Card:
        if not (0 <= idx < len(self.hands[player.name])):
            raise ValueError("Invalid index for exchange.")
        old_card = self.hands[player.name][idx]
        self.hands[player.name][idx] = card
        if reveal:
            player.learn_card(idx, card)
        return old_card

    def penalize(self, player: Player):
        """Give a penalty card to the player and add a None to their view hand."""
        print(f"Player {player.name} is penalized.")
        penalty_card = self.dealer.draw(Dealer.Source.DRAW)
        self.hands[player.name].append(penalty_card)
        player.view.hand.append(None)
        for opponent in self.players:
            if opponent != player:
                opponent.view.opponents_hands[player.name].append(None)

    def reveal_to_others(self, player: Player, idx: int, card: Card):
        # Update all opponents' views
        for opponent in self.players:
            if opponent != player:
                opponent.learn_opponent_card(player, idx, card)

    def allow_discards(self, player: Player, player_relative_speed: int = 5):
        """Allow players to discard a card that is similar to the top of the discard pile.

        Args:
            player (Player): The player who is attempting to discard.
            player_relative_speed (int, optional): The relative speed advantage of the current player. Defaults to 5.
            1 means same speed as opponents, >1 means faster, <1 means slower.
        """
        card = self.dealer.discard_pile[-1] if self.dealer.discard_pile else None
        if card is None:
            return

        # Players want to discard (they can make errors and be penalized)
        while True:  # For chaining discards of special cards
            discard_idx = [
                (p, p.strategy.select_card_to_discard(self.view, p.view))
                for p in self.players
            ]
            discard_idx = [
                (p, idx) for p, idx in discard_idx if 0 <= idx < len(self.hands[p.name])
            ]  # Valid discards
            if discard_idx:
                speeds = [
                    1 if p != player else player_relative_speed for p, _ in discard_idx
                ]

                # Select the fastest player among those who want to discard
                p, idx = random.choices(discard_idx, weights=speeds)[0]
                card_to_discard = self.hands[p.name][idx]
                if card_to_discard != card:
                    print(
                        f"Player {p.name} attempted to discard {card_to_discard}, but top of discard pile is {card}. Penalizing."
                    )
                    self.penalize(p)
                else:
                    self.discard(p, idx)

            if not discard_idx or card.effect == Card.Effect.NONE:
                break

    def apply_effect(self, player: Player, effect: Card.Effect, decision: Any):
        if effect == Card.Effect.DRAW:
            target_name = decision
            target_player = self.get_player_by_name(target_name)
            self.penalize(target_player)

        # TODO: think about how to make it more realistic
        elif effect == Card.Effect.SHUFFLE:
            target_name = decision
            target_player = self.get_player_by_name(target_name)
            random.shuffle(self.hands[target_player.name])
            target_player.view.hand = [None] * len(target_player.view.hand)

        elif effect == Card.Effect.SWAP:
            target_name1, idx1, target_name2, idx2 = decision
            target1 = self.get_player_by_name(target_name1)
            target2 = self.get_player_by_name(target_name2)
            # Swap the cards in the hands
            card1 = self.hands[target1.name][idx1]
            card2 = self.hands[target2.name][idx2]
            self.hands[target1.name][idx1] = card2
            self.hands[target2.name][idx2] = card1
            # Update the views
            for player in self.players:
                if player == target1:
                    tmp = player.view.hand[idx1]
                    player.view.hand[idx1] = player.view.opponents_hands[target2.name][
                        idx2
                    ]
                    player.view.opponents_hands[target2.name][idx2] = tmp
                elif player == target2:
                    tmp = player.view.hand[idx2]
                    player.view.hand[idx2] = player.view.opponents_hands[target1.name][
                        idx1
                    ]
                    player.view.opponents_hands[target1.name][idx1] = tmp
                else:
                    tmp = player.view.opponents_hands[target1.name][idx1]
                    player.view.opponents_hands[target1.name][idx1] = (
                        player.view.opponents_hands[target2.name][idx2]
                    )
                    player.view.opponents_hands[target2.name][idx2] = tmp

        elif effect == Card.Effect.PEEK:
            target_name, idx = decision
            target = self.get_player_by_name(target_name)
            if target == player:
                player.learn_card(idx, self.hands[target.name][idx])
            else:
                player.learn_opponent_card(
                    target, idx, self.hands[target.name][idx]
                )

    def calculate_scores(self):
        """Implement the scoring logic based on the caller and hands."""
        tmp_scores = [
            sum(card.value() for card in self.hands[p.name]) for p in self.players
        ]
        scores = tmp_scores[:]
        caller_score = tmp_scores.pop(self.caller_index)
        min_opponent_score = min(tmp_scores)
        if min_opponent_score > caller_score:
            print(f"Player {self.players[self.caller_index].name} successfully called!")
            scores[self.caller_index] = 0
        else:
            print(f"Player {self.players[self.caller_index].name} failed the call.")
            scores[self.caller_index] *= 2
        for i, _ in enumerate(self.players):
            self.view.scores[i] += scores[i]

    def init_round(self):
        self.dealer.reset_deck()
        self.dealer.deal_initial_hands(self.hands)
        # Player learn their initial hands
        for player in self.players:
            player.view.reset(self, player)
            for i in self.initially_known:
                player.learn_card(i, self.hands[player.name][i])
        # Player with highest score starts
        self.current_player_index = (
            0 if self.round == 0 else self.view.scores.index(max(self.view.scores))
        )
        self.caller_index = -1

    def end_round(self):
        self.view.round += 1
        self.calculate_scores()

    def is_finished(self) -> bool:
        return any(score >= 100 for score in self.view.scores)

    def end_game(self):
        print("## Game Over ##")
        for i, player in enumerate(self.players):
            print(f"Player {player.name}: {self.view.scores[i]} points")
