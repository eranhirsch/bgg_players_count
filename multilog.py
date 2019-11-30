#!/usr/local/bin/python3

import sys
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestThing import RequestThing
from CLIGamesParser import CLIGamesParser
from observers import MultiLog as ml

SEPARATOR = "\t"


def main(argv: List[str] = []) -> int:
    fields = ["Name", "ID"] + ml.Presenter.column_names()
    with open(argv[1], "wt") as output:
        output.write(f"{SEPARATOR.join(fields)}\n")
        output.writelines(process_games(CLIGamesParser(argv[2:])))

    return 0


def process_games(games: Iterable[int]) -> Iterator[str]:
    for index, game_id in enumerate(games):
        game = RequestThing(game_id).with_flags("stats").query_first()

        print(
            f"Processing plays for game {index:03d}: {game.primary_name()} ({game.id()})"
        )

        logic = ml.Logic()
        for plays, play in enumerate(RequestPlays(thingid=game_id).queryAll()):
            logic.visit(play)

        try:
            fields = [game.primary_name(), game.id(), ml.Presenter(logic, SEPARATOR)]
            yield f"{SEPARATOR.join([str(field) for field in fields])}\n"
        except Exception as e:
            print(f"Skipping {game.primary_name()} because: {e}")

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
