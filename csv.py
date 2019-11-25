#!/usr/local/bin/python3

import sys
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Set

from bgg.api.RequestFamily import RequestFamily
from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import PlayerCountAggregator as pca
from observers import SessionCounter as sc

SEPARATOR = "\t"
COLLECTED_FAMILIES: Set[int] = {36963, 39442, 54682, 2580, 25246, 23234}
MIN_PLAYS_FOR_DISPLAY = 50

g_games_in_family: Dict[int, Set[int]] = defaultdict(set)


def main(argv: List[str] = []) -> int:
    fields = (
        ["Name", "ID", "Category", "Year", "Rank", "Published", "Ratings", "Owned"]
        + sc.Presenter.column_names()
        + pca.CSVPresenter.column_names()
    )
    with open(argv[1], "wt") as output:
        output.write(f"{SEPARATOR.join(fields)}\n")
        output.writelines(process_games(CLIGamesParser(argv[2:])))
        output.writelines(process_families())

    return 0


def process_games(games: Iterable[int]) -> Iterator[str]:
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

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        player_count_logic = pca.Logic()
        session_count_logic = sc.Logic()
        for plays, play in enumerate(RequestPlays(thingid=game_id).queryAll()):
            player_count_logic.visit(play)
            session_count_logic.visit(play)

        if plays >= MIN_PLAYS_FOR_DISPLAY:
            try:
                fields = [
                    game.primary_name(),
                    game.id(),
                    game.primary_category() or "",
                    game.year_published(),
                    game.overall_rank(),
                    f"{game.player_count()[0]}-{game.player_count()[1]}",
                    game.ratings().users_rated(),
                    game.ratings().market()[0],
                    sc.Presenter(session_count_logic),
                    pca.CSVPresenter(player_count_logic, SEPARATOR),
                ]
                yield f"{SEPARATOR.join([str(field) for field in fields])}\n"
            except Exception as e:
                print(f"Skipping {game.primary_name()} because: {e}")
        else:
            print(
                f"Game {game.primary_name()} ({game.id()}) only had {plays} plays so it won't be added to the output!"
            )

    print(f"Finished processing {index-1} games")


def process_families() -> Iterator[str]:
    for family_id, family_games in g_games_in_family.items():
        if not family_games:
            raise Exception(f"Family {family_id} has no entries in it!")

        yield process_family(family_id, family_games)

    print(f"Finished processing all families")


def process_family(id: int, family_games: Iterable[int]) -> str:
    family = RequestFamily(id).query_first()

    player_count_logic = pca.Logic()
    session_count_logic = sc.Logic()

    earliest_year = None
    popular_category = None
    best_rank = None
    published_play_count = None
    popular_users_rated = 0
    total_owned = 0
    for index, game_id in enumerate(family_games):
        game = RequestThing(game_id).with_flags("stats").query_first()

        print(
            f"Adding {index:03d} {game.primary_name()} ({game.id()}) to family {family.primary_name()}"
        )

        if game.ratings().users_rated() > popular_users_rated:
            popular_users_rated = game.ratings().users_rated()
            if game.type() == "boardgame":
                # expansions don't have categories
                if game.primary_category():
                    popular_category = game.primary_category()
                if game.overall_rank():
                    best_rank = game.overall_rank()
                published_play_count = game.player_count()

        if not earliest_year or game.year_published() < earliest_year:
            earliest_year = game.year_published()

        total_owned += game.ratings().market()[0]

        for play in RequestPlays(thingid=game_id).queryAll():
            player_count_logic.visit(play)
            session_count_logic.visit(play)

    print(
        f"Finished processing family {family.primary_name()}, it has {index-1} games in it"
    )

    published = (
        f"{published_play_count[0]}-{published_play_count[1]}"
        if published_play_count
        else "Unknown"
    )

    fields = [
        # I don't use the word family here because it would clash with the
        # family category
        f"{family.primary_name()} [SERIES]",
        family.id(),
        popular_category or "",
        earliest_year,
        best_rank,
        published,
        popular_users_rated,
        total_owned,
        sc.Presenter(session_count_logic),
        pca.CSVPresenter(player_count_logic, SEPARATOR),
    ]
    return f"{SEPARATOR.join([str(field) for field in fields])}\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
