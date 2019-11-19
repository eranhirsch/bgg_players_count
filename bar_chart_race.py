#!/usr/local/bin/python3

import datetime
import sys
import unicodedata
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import BarChartRace as bcr

SEPARATOR = "\t"


def main(argv: List[str] = []) -> int:
    aggr_by = int(argv[2])
    with open(argv[1], "wt") as output:
        output.write(
            f"{SEPARATOR.join(['Name', 'Category', 'Image'] + bcr.Presenter.column_names(window(aggr_by)))}\n"
        )
        output.writelines(process_games(aggr_by, CLIGamesParser(argv[3:])))
    return 0


def window(aggr_by: int) -> bcr.DateRange:
    return bcr.DateRange(
        bcr.Month(2000, aggr_by),
        bcr.Month.fromDate(datetime.date.today()),
        step=aggr_by,
    )


def process_games(aggr_by: int, games: Iterable[int]) -> Iterator[str]:
    index = 1
    for game_id in games:
        game = RequestThing(game_id).query(with_stats=True).only_item()
        if game.type() != "boardgame":
            print(f"Skipping '{game.type()}': {game.primary_name()} ({game.id()})")
            continue

        name = (
            unicodedata.normalize("NFKD", game.primary_name())
            .encode("ascii", "ignore")
            .decode("ascii")
        )

        metadata = [
            f"{game.year_published()}-{name}",
            game.primary_category() or "",
            game.thumbnail() or "",
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        bar_chart_race = bcr.Logic(aggr_by)
        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

        yield f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, window(aggr_by), SEPARATOR).render()}\n"

        index += 1

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
