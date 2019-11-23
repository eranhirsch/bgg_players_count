#!/usr/local/bin/python3

import sys
from typing import List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import PlayerCountAggregator as pca
from observers import QuantityNormalizer as qn
from observers.LocationsCountLogic import (
    LocationsCountCLIPresenter,
    LocationsCountLogic,
)


def main(argv: List[str] = []) -> int:
    player_count_logic = pca.Logic()
    locations_logic = LocationsCountLogic()
    quantity_logic = qn.Logic()

    try:
        index = 1
        for game_id in CLIGamesParser(argv[1:]):
            game = RequestThing(game_id).query().only_item()
            print(
                f"Processing plays for game {index:03d}: {game.primary_name()} ({game_id})"
            )
            for play in RequestPlays(thingid=game_id).queryAll():
                player_count_logic.visit(play)
                locations_logic.visit(play)
                quantity_logic.visit(play)
            index += 1

        print(f"Finished processing")
        return 0

    finally:
        print(pca.CLIPresenter(player_count_logic))
        print("\n" * 3)
        print(LocationsCountCLIPresenter(locations_logic, is_digital=False))
        print("\n")
        print(LocationsCountCLIPresenter(locations_logic, is_digital=True))
        print("\n")
        print(qn.Presenter(quantity_logic, percentile=0.99))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
