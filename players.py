#!/usr/local/bin/python3

import sys
from typing import List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import LocationsCount as lc
from observers import PlayerCountAggregator as pca
from observers import QuantityNormalizer as qn


def main(argv: List[str] = []) -> int:
    locations_logic = lc.Logic()
    quantity_logic = qn.Logic()

    try:
        for index, game_id in enumerate(CLIGamesParser(argv[1:])):
            game = RequestThing(game_id).with_flags("stats").query_first()
            print(
                f"Processing plays for game {index:03d}: {game.primary_name()} ({game_id})"
            )
            player_count_logic = pca.Logic(game.player_count())
            for play in RequestPlays(thingid=game_id).queryAll():
                player_count_logic.visit(play)
                locations_logic.visit(play)
                quantity_logic.visit(play)

        print(f"Finished processing")
        return 0

    finally:
        print(pca.CLIPresenter(player_count_logic))
        print("\n" * 3)
        print(lc.CLIPresenter(locations_logic, is_digital=False))
        print("\n")
        print(lc.CLIPresenter(locations_logic, is_digital=True))
        print("\n")
        print(qn.Presenter(quantity_logic, percentile=0.99))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
