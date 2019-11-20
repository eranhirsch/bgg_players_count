#!/usr/local/bin/python3

import sys
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers.PlayerCountAggregatorLogic import (
    PlayerCountAggregatorCSVPresenter,
    PlayerCountAggregatorLogic,
)

SEPARATOR = "\t"


def main(argv: List[str] = []) -> int:
    with open(argv[1], "wt") as output:
        output.write(
            f"{SEPARATOR.join(['Name', 'ID', 'Category', 'Year', 'Rank', 'Published', 'Ratings', 'Owned'] + PlayerCountAggregatorCSVPresenter.column_names())}\n"
        )
        output.writelines(process_games(CLIGamesParser(argv[2:])))
    return 0


def process_games(games: Iterable[int]) -> Iterator[str]:
    index = 1
    for game_id in games:
        game = RequestThing(game_id).query(with_stats=True).only_item()
        if game.type() != "boardgame":
            print(f"Skipping '{game.type()}': {game.primary_name()} ({game.id()})")
            continue

        metadata = [
            game.primary_name(),
            f"{game.id()}",
            game.primary_category() or "",
            f"{game.year_published()}",
            f"{game.overall_rank()}",
            f"{game.player_count()[0]}-{game.player_count()[1]}",
            f"{game.ratings().users_rated()}",
            f"{game.ratings().market()[0]}",
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        player_count_logic = PlayerCountAggregatorLogic()
        for play in RequestPlays(thingid=game_id).queryAll():
            player_count_logic.visit(play)

        try:
            yield f"{SEPARATOR.join(metadata)}{SEPARATOR}{PlayerCountAggregatorCSVPresenter(player_count_logic, SEPARATOR).render()}\n"
        except Exception as e:
            print(f"Skipping {game.primary_name()} because: {e}")

        index += 1

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
