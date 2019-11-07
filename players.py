#!/usr/local/bin/python3

import sys
from typing import Iterator, List

from bgg.api.RequestList import RequestList
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

LIST_PREFIX = "list-"


def main(argv: List[str] = []) -> int:
    player_count_logic = PlayerCountAggregatorLogic()
    locations_logic = LocationsCountLogic()

    try:
        index = 1
        for game_id in extract_game_ids_from_input(argv[1:]):
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


def extract_game_ids_from_input(user_inputs: List[str]) -> Iterator[int]:
    for user_input in user_inputs:
        if user_input.startswith(LIST_PREFIX):
            listid = int(user_input.split(LIST_PREFIX)[1])
            geeklist = RequestList(listid).fetch()
            print(
                f'Iterating over geeklist "{geeklist.title()}" by {geeklist.user_name()} [last updated: {geeklist.edit_date()}]'
            )

            for item in geeklist.filter(("thing", "boardgame")):
                yield item.object_id()

            print(f"Finished GeekList {geeklist.id()}")

        elif user_input.isdigit():
            yield int(user_input)

        else:
            yield get_game_id_from_name(user_input)


def get_game_id_from_name(user_input: str) -> int:
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
