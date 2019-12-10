#!/usr/local/bin/python3

import datetime
import sys
import unicodedata
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Set, Tuple

from bgg.api.RequestFamily import RequestFamily
from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import BarChartRace as bcr

SEPARATOR = "\t"
MISSING_CATEGORY_LABEL = "[Unknown]"
MISSING_YEAR_LABEL = "????"
COLLECTED_FAMILIES: Set[int] = {
    2,  # Carcassonne
    3,  # Catan
    8,  # Fluxx
    17,  # Ticket to Ride
    34,  # Axis & Allies
    62,  # Advanced Squad Leader
    71,  # Cluedo
    100,  # Monopoly
    2580,  # Dominion
    3430,  # Pandemic
    4571,  # Race for the Galaxy
    4711,  # Scrabble
    5723,  # War of the Rings
    7687,  # Summoner Wars
    8878,  # Time's Up
    9644,  # Dixit
    9768,  # BattleLore
    9974,  # Ascension
    10552,  # CaSh 'n Gun$
    10782,  # Timeline
    12926,  # Wits and Wagers
    18113,  # Star Wars X-Wing
    22707,  # Cards Against Humanity
    23234,  # Pathfinder
    24962,  # Hive
    25246,  # Star Realms
    27123,  # Love Letter
    27945,  # One Night
    28525,  # King of Tokyo
    35759,  # T.I.M.E Stories
    36963,  # Exit: The Game
    37062,  # Codenames
    39442,  # Unlock
    39723,  # Forbidden Games
    44820,  # Sushi Go
    46771,  # Champions of Midgard
    47479,  # Century Trilogy
    48927,  # Clank!
    50195,  # Kingdomino
    54060,  # Betrayal Family
    54682,  # KeyForge
    56924,  # Risk (Official)
    57039,  # Azul
    57498,  # Through the Ages
    57499,  # Brass
    57505,  # Mansions of Madness
    57676,  # Railroad Ink
}

g_games_in_family: Dict[int, Set[int]] = defaultdict(set)


def main(argv: List[str] = []) -> int:
    aggr_by = int(argv[3])

    with open(argv[1], "wt") as plays_output:
        with open(argv[2], "wt") as users_output:
            plays_output.write(
                f"{SEPARATOR.join(['Name', 'Category', 'Image', '1999-12-31'] + bcr.Presenter.column_names(window(aggr_by)))}\n"
            )
            users_output.write(
                f"{SEPARATOR.join(['Name', 'Category', 'Image', '1999-12-31'] + bcr.Presenter.column_names(window(aggr_by)))}\n"
            )
            for plays, users in process_games(aggr_by, CLIGamesParser(argv[4:])):
                plays_output.write(plays)
                users_output.write(users)
            for plays, users in process_families(aggr_by):
                plays_output.write(plays)
                users_output.write(users)

            total_fields = [
                "TOTAL",
                MISSING_CATEGORY_LABEL,
                "",
                MISSING_YEAR_LABEL,
                bcr.Presenter(bcr.TotalUsersLogic(), window(aggr_by), 1999, SEPARATOR),
            ]
            users_output.write(
                f"{SEPARATOR.join([str(field) for field in total_fields])}\n"
            )

    return 0


def window(aggr_by: int) -> bcr.DateRange:
    return bcr.DateRange(
        bcr.Month(2000, aggr_by),
        bcr.Month.fromDate(datetime.date.today()),
        step=aggr_by,
    )


def normalize_str(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def process_games(aggr_by: int, games: Iterable[int]) -> Iterator[Tuple[str, str]]:
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
            f"{game.year_published() or MISSING_YEAR_LABEL}-{normalize_str(game.primary_name())}",
            game.primary_category() or MISSING_CATEGORY_LABEL,
            game.thumbnail() or "",
            "0",
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        plays_logic = bcr.UniquePlaysLogic(aggr_by)
        users_logic = bcr.UniqueUsersLogic(aggr_by)
        total_logic = bcr.TotalUsersLogic(aggr_by)
        for play in RequestPlays(thingid=game_id).queryAll():
            plays_logic.visit(play)
            users_logic.visit(play)
            total_logic.visit(play)

        for exp_index, expansion in enumerate(game.links()["boardgameexpansion"]):
            print(
                f"Fetching plays for expansion {exp_index:02d}: {expansion[1]} ({expansion[0]}) of {game.primary_name()}"
            )
            for play in RequestPlays(thingid=expansion[0]).queryAll():
                plays_logic.visit(play)
                users_logic.visit(play)

        yield (
            f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(plays_logic, window(aggr_by), game.year_published(), SEPARATOR)}\n",
            f"{SEPARATOR.join(metadata)}{SEPARATOR}{bcr.Presenter(users_logic, window(aggr_by), game.year_published(), SEPARATOR)}\n",
        )

    print(f"Finished processing {index-1} games")


def process_families(aggr_by: int) -> Iterator[Tuple[str, str]]:
    for family_id, family_games in g_games_in_family.items():
        if not family_games:
            raise Exception(f"Family {family_id} has no entries in it!")

        process_family(aggr_by, family_id, family_games, bcr.TotalUsersLogic(aggr_by))
        yield (
            process_family(
                aggr_by, family_id, family_games, bcr.UniquePlaysLogic(aggr_by)
            ),
            process_family(
                aggr_by, family_id, family_games, bcr.UniqueUsersLogic(aggr_by)
            ),
        )

    print(f"Finished processing all families")


def process_family(
    aggr_by: int, id: int, family_games: Iterable[int], bar_chart_race: bcr.MonthlyLogic
) -> str:
    family = RequestFamily(id).query_first()

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

        if game.year_published() and (
            not earliest_year or game.year_published() < earliest_year
        ):
            earliest_year = game.year_published()

        for play in RequestPlays(thingid=game_id).queryAll():
            bar_chart_race.visit(play)

    metadata = [
        # I don't use the word family here because it would clash with the
        # family category
        f"[SERIES] {earliest_year or MISSING_YEAR_LABEL}-{normalize_str(family.primary_name())}",
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
