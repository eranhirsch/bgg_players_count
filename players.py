#!/usr/local/bin/python3

import sys
from typing import List

from bgg.api.RequestPlays import RequestPlays
from CLIGamesParser import CLIGamesParser
from observers.LocationsCountLogic import (
    LocationsCountCLIPresenter,
    LocationsCountLogic,
)
from observers.PlayerCountAggregatorLogic import (
    PlayerCountAggregatorCLIPresenter,
    PlayerCountAggregatorLogic,
)


def main(argv: List[str] = []) -> int:
    player_count_logic = PlayerCountAggregatorLogic()
    locations_logic = LocationsCountLogic()

    try:
        index = 1
        for game_id in CLIGamesParser(argv[1:]):
            print(f"Processing plays for game {index:03d}: ID={game_id}")
            for play in RequestPlays(thingid=game_id).queryAll():
                player_count_logic.visit(play)
                locations_logic.visit(play)
            index += 1

        print(f"Finished processing")
        return 0

    finally:
        print(PlayerCountAggregatorCLIPresenter(player_count_logic).render())
        print("\n" * 3)
        print(LocationsCountCLIPresenter(locations_logic).render(is_digital=False))
        print("\n")
        print(LocationsCountCLIPresenter(locations_logic).render(is_digital=True))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
