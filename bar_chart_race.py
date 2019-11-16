#!/usr/local/bin/python3

import sys
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import BarChartRace as bcr

SEPARATOR = "\t"

WINDOW = bcr.DateRange(bcr.Month(2003, 9), bcr.Month(2020, 1))


def main(argv: List[str] = []) -> int:
    with open(argv[1], "wt") as output:
        output.write(
            f"{SEPARATOR.join(['Name', 'Category', 'Image'] + bcr.Presenter.column_names(WINDOW))}\n"
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
            f"{game.year_published()}-{game.primary_name()}",
            game.primary_category() or "",
            game.thumbnail(),
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        bar_chart_race = bcr.Logic()
        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

        yield f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, WINDOW, SEPARATOR).render()}\n"

        index += 1

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
