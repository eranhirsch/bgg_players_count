#!/usr/local/bin/python3

import sys
from typing import Dict

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestSearch import RequestSearch
from bgg.utils import firstx


def formatResults(player_count_aggr: Dict[int, int]) -> str:
    missing = player_count_aggr[0]
    max_count = max(player_count_aggr.keys())
    total_plays = sum(player_count_aggr.values())
    out = ["Players\tPlays\tRatio\tRatio (No Unknowns)"]
    for player_count in range(max_count):
        plays_count = player_count_aggr[player_count] or 0
        if player_count == 0:
            label = "Unknown\t"
        elif player_count == 1:
            label = "Solo\t"
        else:
            label = f"{player_count} Players"
        ratio = round(100 * (plays_count / total_plays))
        ratio_no_unknowns = (
            round(100 * (plays_count / (total_plays - missing)))
            if player_count > 0
            else 0
        )
        out.append(f"{label}\t{plays_count}\t{ratio}%\t{ratio_no_unknowns}%")
    out.append(f"Total:\t\t{total_plays}")
    return "\n".join(out)


def main(argv=[]) -> int:
    if len(argv) > 1:
        game_input = argv[1]
        if not game_input.isdigit():
            results = RequestSearch().ofType("boardgame").query(game_input)
            if not results:
                raise Exception(f"No game found with the name '{game_input}'")

            result = firstx(results)
            if len(results) == 1:
                print(f"Game found (as '{result.name()[0]}'")
            else:
                print(
                    f"More than one entry found, using '{result.name()[0]}' published in {result.yearPublished()}"
                )
            id = result.id()
        else:
            id = int(game_input)
    else:
        # Innovation, just for fun...
        id = 63888
    print(f"Processing plays for: ID={id}")

    player_count_aggr: Dict[int, int] = {}
    try:
        for play in RequestPlays().forID(id).queryAll():
            players = play.players() or []
            player_count = len(players)
            try:
                player_count_aggr[player_count] += play.quantity()
            except KeyError:
                player_count_aggr[player_count] = play.quantity()
        return 0
    except Exception:
        print(f"Encountered exception while processing")
        raise
    finally:
        print(formatResults(player_count_aggr))

    print(f"Finished processing")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
