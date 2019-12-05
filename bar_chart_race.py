#!/usr/local/bin/python3

import datetime
import sys
import unicodedata
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Set

from bgg.api.RequestFamily import RequestFamily
from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import BarChartRace as bcr

SEPARATOR = "\t"
MISSING_CATEGORY_LABEL = "[Unknown]"
COLLECTED_FAMILIES: Set[int] = {
    2,  # Carcassonne
    8,  # Fluxx
    17,  # Ticket to Ride
    34,  # Axis & Allies
    62,  # Advanced Squad Leader
    100,  # Monopoly
    2580,  # Dominion
    7687,  # Summoner Wars
    8878,  # Time's Up
    9644,  # Dixit
    9974,  # Ascension
    10782,  # Timeline
    18113,  # Star Wars X-Wing
    22707,  # Cards Against Humanity
    23234,  # Pathfinder
    25246,  # Star Realms
    27123,  # Love Letter
    27945,  # One Night
    36963,  # Exit: The Game
    39442,  # Unlock
    54682,  # KeyForge
    57039,  # Azul
}

g_games_in_family: Dict[int, Set[int]] = defaultdict(set)


def get_logic(aggr_by: int) -> bcr.MonthlyLogic:
    return bcr.UniquePlaysLogic(aggr_by)


def main(argv: List[str] = []) -> int:
    aggr_by = int(argv[2])
    with open(argv[1], "wt") as output:
        output.write(
            f"{SEPARATOR.join(['Name', 'Category', 'Image', '1999-12-31'] + bcr.Presenter.column_names(window(aggr_by)))}\n"
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
    for index, game_id in enumerate(games):
        game = RequestThing(game_id).with_flags("stats").query_first()

        collected_families = [
            family_id
            for family_id, family_name in game.links()["boardgamefamily"]
            if family_id in COLLECTED_FAMILIES
        ]
        if collected_families:
            collected_family = collected_families[0]
            g_games_in_family[collected_family].add(game.id())
            print(
                f"Skipping '{game.primary_name()}' ({game.id()}). It is part of family: {collected_family}"
            )
            continue

        if game.type() != "boardgame":
            print(f"Skipping '{game.type()}': {game.primary_name()} ({game.id()})")
            continue

        metadata = [
            f"{game.year_published()}-{normalize_str(game.primary_name())}",
            game.primary_category() or MISSING_CATEGORY_LABEL,
            game.thumbnail() or "",
            "0",
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        bar_chart_race = get_logic(aggr_by)
        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

        for exp_index, expansion in enumerate(game.links()["boardgameexpansion"]):
            print(
                f"Fetching plays for expansion {exp_index:02d}: {expansion[1]} ({expansion[0]}) of {game.primary_name()}"
            )
            for play in RequestPlays(thingid=expansion[0]).queryAll():
                bar_chart_race.visit(play)

        yield f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, window(aggr_by), game.year_published(), SEPARATOR)}\n"

    print(f"Finished processing {index-1} games")


def process_families(aggr_by: int) -> Iterator[str]:
    for family_id, family_games in g_games_in_family.items():
        if not family_games:
            raise Exception(f"Family {family_id} has no entries in it!")

        yield process_family(aggr_by, family_id, family_games)

    print(f"Finished processing all families")


def process_family(aggr_by: int, id: int, family_games: Iterable[int]) -> str:
    family = RequestFamily(id).query_first()

    bar_chart_race = get_logic(aggr_by)

    earliest_year = None
    popular_category = None
    popular_thumbnail = None
    popular_users_rated = 0
    for index, game_id in enumerate(family_games):
        game = RequestThing(game_id).with_flags("stats").query_first()

        print(
            f"Adding {index:03d} {game.primary_name()} ({game.id()}) to family {family.primary_name()}"
        )

        if (
            game.type() == "boardgame"
            and game.primary_category()
            and (
                not popular_category
                or game.ratings().users_rated() > popular_users_rated
            )
        ):
            popular_category = game.primary_category()

        if game.ratings().users_rated() > popular_users_rated:
            popular_users_rated = game.ratings().users_rated()
            popular_thumbnail = game.thumbnail()

        if not earliest_year or game.year_published() < earliest_year:
            earliest_year = game.year_published()

        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

    metadata = [
        # I don't use the word family here because it would clash with the
        # family category
        f"[SERIES] {earliest_year}-{normalize_str(family.primary_name())}",
        popular_category or MISSING_CATEGORY_LABEL,
        family.thumbnail() or popular_thumbnail or "",
        "0",
    ]

    print(
        f"Finished processing family {family.primary_name()}, it has {index+1} games in it"
    )

    return f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(bar_chart_race, window(aggr_by), earliest_year or 1999, SEPARATOR)}\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
