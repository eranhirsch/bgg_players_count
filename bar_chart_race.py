#!/usr/local/bin/python3

import datetime
import sys
import unicodedata
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Set

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import BarChartRace as bcr

SEPARATOR = "\t"
MISSING_CATEGORY_LABEL = "[Unknown]"
COLLECTED_FAMILIES: Set[int] = {36963, 39442, 54682}
MIN_PLAYS_FOR_DISPLAY = 10

g_games_in_family: Dict[str, Set[int]] = defaultdict(set)


def main(argv: List[str] = []) -> int:
    aggr_by = int(argv[2])
    with open(argv[1], "wt") as output:
        output.write(
            f"{SEPARATOR.join(['Name', 'Category', 'Image'] + bcr.Presenter.column_names(window(aggr_by)))}\n"
        )
        output.writelines(process_games(aggr_by, CLIGamesParser(argv[3:])))
        output.writelines(process_families(aggr_by))
    return 0


def window(aggr_by: int) -> bcr.DateRange:
    return bcr.DateRange(
        bcr.Month(2000, aggr_by),
        bcr.Month.fromDate(datetime.date.today()),
        step=aggr_by,
    )


def normalize_str(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def process_games(aggr_by: int, games: Iterable[int]) -> Iterator[str]:
    index = 1
    for game_id in games:
        game = RequestThing(game_id).query(with_stats=True).only_item()
        if game.type() != "boardgame":
            print(f"Skipping '{game.type()}': {game.primary_name()} ({game.id()})")
            continue

        collected_families = [
            family_entry[1]
            for family_entry in game.links()["boardgamefamily"]
            if family_entry[0] in COLLECTED_FAMILIES
        ]
        if collected_families:
            collected_family = collected_families[0]
            g_games_in_family[collected_family].add(game.id())
            print(
                f"Skipping '{game.primary_name()}' ({game.id()}). It is part of family: {collected_family}"
            )
            continue

        metadata = [
            f"{game.year_published()}-{normalize_str(game.primary_name())}",
            game.primary_category() or MISSING_CATEGORY_LABEL,
            game.thumbnail() or "",
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        bar_chart_race = bcr.Logic(aggr_by)
        plays = 0
        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)
            plays += 1

        if plays >= MIN_PLAYS_FOR_DISPLAY:
            yield f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, window(aggr_by), SEPARATOR)}\n"
        else:
            print(
                f"Game {game.primary_name()} ({game.id()}) only had {plays} plays so it won't be added to the output!"
            )

        index += 1

    print(f"Finished processing {index-1} games")


def process_families(aggr_by: int) -> Iterator[str]:
    for family_name, family_games in g_games_in_family.items():
        if not family_games:
            raise Exception(f"Family {family_name} has no entries in it!")

        yield process_family(aggr_by, family_name, family_games)

    print(f"Finished processing all families")


def process_family(aggr_by: int, family_name: str, family_games: Iterable[int]) -> str:
    bar_chart_race = bcr.Logic(aggr_by)

    earliest_year = None
    popular_category = None
    popular_thumbnail = None
    popular_users_rated = 0
    index = 1
    for game_id in family_games:
        game = RequestThing(game_id).query(with_stats=True).only_item()

        print(
            f"Adding {index:03d} {game.primary_name()} ({game.id()}) to family {family_name}"
        )

        if game.ratings().users_rated() > popular_users_rated:
            popular_users_rated = game.ratings().users_rated()
            popular_category = game.primary_category()
            popular_thumbnail = game.thumbnail()

        if not earliest_year or game.year_published() < earliest_year:
            earliest_year = game.year_published()

        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

        index += 1

    metadata = [
        f"{earliest_year}-{normalize_str(family_name)}",
        popular_category or MISSING_CATEGORY_LABEL,
        popular_thumbnail or "",
    ]

    print(f"Finished processing family {family_name}, it has {index-1} games in it")

    return f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, window(aggr_by), SEPARATOR)}\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
