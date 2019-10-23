#!/usr/local/bin/python3.7

import sys
from typing import Dict

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestSearch import RequestSearch
from bgg.utils import firstx

# Just some random game for testing
GAME_ID_INNOVATION = 63888


def main(argv=[]) -> int:
    id = extractGameIDFromUserInput(argv[1]) if len(argv) > 1 else GAME_ID_INNOVATION
    print(f"Processing plays for: ID={id}")

    player_count_aggr: Dict[int, int] = {}
    locations: Dict[str, int] = {}
    try:
        for play in RequestPlays().forID(id).queryAll():
            players = play.players() or []
            player_count = len(players)
            try:
                player_count_aggr[player_count] += play.quantity()
            except KeyError:
                player_count_aggr[player_count] = play.quantity()

            location = play.location().lower()
            try:
                locations[location] += 1
            except KeyError:
                locations[location] = 1

        return 0
    except Exception:
        print(f"Encountered exception while processing")
        raise
    finally:
        print(formatResults(player_count_aggr))
        print(formatLocations(locations))

    print(f"Finished processing")


def extractGameIDFromUserInput(user_input: str) -> int:
    if user_input.isdigit():
        return int(user_input)

    results = RequestSearch().ofType("boardgame").query(user_input)
    if not results:
        raise Exception(f"No game found with the name '{user_input}'")

    result = firstx(results)
    if len(results) == 1:
        print(f"Game found (as '{result.name()[0]}')")
    else:
        print(
            f"More than one entry found, using '{result.name()[0]}' published in {result.yearPublished()}"
        )
    return result.id()


def formatResults(player_count_aggr: Dict[int, int]) -> str:
    missing = player_count_aggr[0]
    max_count = max(player_count_aggr.keys())
    total_plays = sum(player_count_aggr.values())
    out = ["Players\t\tPlays\tRatio\tRatio (No Unknowns)"]
    for players in range(max_count + 1):
        plays = player_count_aggr.get(players, 0)
        if players == 0:
            label = "Unknown\t"
        elif players == 1:
            label = "Solo\t"
        else:
            label = f"{players} Players"
        ratio = plays / total_plays
        ratio_no_unknowns = plays / (total_plays - missing) if players > 0 else 0
        out.append(
            f"{label}\t{plays}\t{100*ratio:2.0f}%\t{100*ratio_no_unknowns:2.0f}%"
        )
    out.append(f"Total:\t\t{total_plays}")
    return "\n".join(out)


def formatLocations(locations: Dict[str, int]) -> str:
    return "\n".join(
        [
            f"{location}\t{count}"
            for count, location in sorted(
                [
                    (location, count)
                    for location, count in locations.items()
                    if location != "" and count > 1
                ],
                key=lambda item: item[1],
                reverse=True,
            )[:10]
        ]
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
