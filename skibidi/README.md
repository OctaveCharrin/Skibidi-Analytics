# Skibidi Game Analytics Engine

**Skibidi Analytics** is a Python-based simulation engine designed for analyzing and comparing strategies for the Skibidi card game. It provides a clean, modular architecture that separates the game logic from player decision-making, allowing for robust testing and analysis of different play styles.

The core of the engine is the `Game` class, which orchestrates the game flow, while individual player actions are dictated by interchangeable `Strategy` classes.

## Core Architecture

The system is designed to mimic a client-server model where the `Game` acts as the authoritative server and each `Player` acts as a client. Players make decisions based on a limited view of the game state, ensuring that strategies cannot "cheat" by accessing hidden information.

### Public Game View (`Game.View`)

This object represents the shared state of the game that is visible to all players. It is accessible via `game.view` and contains the following information:

-   **`dealer_view` (`Dealer.View`)**: A public view of the dealer's state.
    -   `draw_pile_size` (`int`): The number of cards remaining in the draw pile.
    -   `discard_pile` (`list[Card]`): The list of cards in the discard pile, with the most recently discarded card at the end.
-   **`effects_queue` (`list[tuple[Player, Card.Effect]]`)**: A queue of card effects that have been triggered and are waiting to be resolved.
-   **`scores` (`list[int]`)**: The current total scores for all players in the game.
-   **`round` (`int`)**: The current round number.

### Player's Private View (`Player.View`)

This object represents the unique knowledge of a single player. It contains everything they know about their own hand, the cards they've seen, and what they've inferred about their opponents' hands. It is accessible via `player.view`.

-   **`drawn_card` (`Card | None`)**: The card most recently drawn by the player, which they must decide to either keep or discard.
-   **`hand` (`list[Card | None]`)**: The player's own hand. Cards the player has not yet seen are represented as `None`.
-   **`opponents_hands` (`dict[str, list[Card | None]]`)**: A dictionary mapping each opponent's name to a list representing their hand. `None` indicates an unknown card.
-   **`treasure` (`list[Card | None]`)**: The player's knowledge of the treasure cards.

## Implementing a Custom Strategy

To analyze game outcomes, you can create custom strategies by inheriting from the abstract base class `skibidi.strategy.Strategy`. Each method in your custom class will receive the public `Game.View` and the player's private `Player.View` as input and must return a specific decision.

### Strategy Method Guide

Here is how to implement each required method:

#### 1. `select_draw_pile(public, private)`
-   **Purpose**: Decide whether to draw from the draw pile or the discard pile.
-   **Returns**: `Dealer.Source.DRAW` or `Dealer.Source.DISCARD`.

#### 2. `select_card_to_exchange(public, private, source)`
-   **Purpose**: After drawing a card, decide which card in your hand to replace.
-   **Returns**:
    -   An `int` representing the index of the card in your hand to swap out.
    -   `-1` if you wish to discard the newly drawn card instead of keeping it.

#### 3. `select_card_to_discard(public, private)`
-   **Purpose**: Decide which card from your hand to discard when an opportunity arises (e.g., matching the top of the discard pile).
-   **Returns**:
    -   The `int` index of the card to discard.
    -   `-1` if you choose not to discard.

#### 4. `decide_call(public, private)`
-   **Purpose**: Decide whether to "call" to end the round.
-   **Returns**:
    -   The `int` index of a card to discard upon calling.
    -   `-1` if you do not wish to call.
    -   **Note**: If you have only one card left, you must still return a valid index (e.g., `0`) to signal the call, even though the card won't be discarded.

#### 5. `decide_effect(public, private, effect)`
-   **Purpose**: Provide the necessary input to resolve a card's special effect.
-   **Returns**: The return type depends on the `effect` being resolved.
    -   **`DRAW` or `SHUFFLE`**: Return the target player's name as a `str`.
    -   **`PEEK`**: Return a `tuple(target_player_name: str, card_index: int)`.
    -   **`SWAP`**: Return a `tuple(player1_name: str, card1_index: int, player2_name: str, card2_index: int)`.
    -   **`NONE`**: No decision is needed; you can return `None`.
