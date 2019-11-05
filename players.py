#!/usr/local/bin/python3

import sys

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestSearch import RequestSearch
from bgg.utils import firstx
from observers.LocationsCountLogic import (
    LocationsCountCLIPresenter,
    LocationsCountLogic,
)
from observers.PlayerCountAggregatorLogic import (
    PlayerCountAggregatorCLIPresenter,
    PlayerCountAggregatorLogic,
)


def main(argv=[]) -> int:
    id = extractGameIDFromUserInput(argv[1])
    print(f"Processing plays for: ID={id}")

    player_count_logic = PlayerCountAggregatorLogic()
    locations_logic = LocationsCountLogic()

    try:
        for play in RequestPlays(thingid=id).queryAll():
            player_count_logic.visit(play)
            locations_logic.visit(play)

        print(f"Finished processing")
        return 0

    finally:
        print(PlayerCountAggregatorCLIPresenter(player_count_logic).render())
        print("\n" * 3)
        print(LocationsCountCLIPresenter(locations_logic).render(is_digital=False))
        print("\n")
        print(LocationsCountCLIPresenter(locations_logic).render(is_digital=True))


def extractGameIDFromUserInput(user_input: str) -> int:
    if user_input.isdigit():
        return int(user_input)

    results = RequestSearch().ofType("boardgame").query(user_input)
    result = firstx(results)
    if len(results) == 1:
        print(f"Game found (as '{result.name()[0]}')")
    else:
        print(
            f"More than one entry found, using '{result.name()[0]}' published in {result.yearPublished()}"
        )
    return result.id()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
