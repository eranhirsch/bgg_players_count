#!/usr/local/bin/python3

import sys
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import PlayerCountAggregator as pca
from observers import SessionCounter as sc

SEPARATOR = "\t"


def main(argv: List[str] = []) -> int:
    fields = (
        ["Name", "ID", "Category", "Year", "Rank", "Published", "Ratings", "Owned"]
        + pca.CSVPresenter.column_names()
        + sc.Presenter.column_names()
    )
    with open(argv[1], "wt") as output:
        output.write(f"{SEPARATOR.join(fields)}\n")
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
            game.id(),
            game.primary_category() or "",
            game.year_published(),
            game.overall_rank(),
            f"{game.player_count()[0]}-{game.player_count()[1]}",
            game.ratings().users_rated(),
            game.ratings().market()[0],
        ]

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        player_count_logic = pca.Logic()
        session_count_logic = sc.Logic()
        for play in RequestPlays(thingid=game_id).queryAll():
            player_count_logic.visit(play)
            session_count_logic.visit(play)

        try:
            fields = metadata + [
                sc.Presenter(session_count_logic),
                pca.CSVPresenter(player_count_logic, SEPARATOR),
            ]
            yield f"{SEPARATOR.join([str(field) for field in fields])}\n"
        except Exception as e:
            print(f"Skipping {game.primary_name()} because: {e}")

        index += 1

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
