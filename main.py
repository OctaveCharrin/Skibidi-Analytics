import logging
from skibidi.game import Game
from skibidi.strategy.human import HumanStrategy
from skibidi.strategy.random import RandomStrategy

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    game = Game(
        names=["Alex", "Eiji", "Hugo", "Leo", "Octave"],
        verbose=True,
    )
    for i, player in enumerate(game.players):
        # Octave does not play randomly !
        player.strategy = HumanStrategy() if i == 4 else RandomStrategy()
    game.play()
