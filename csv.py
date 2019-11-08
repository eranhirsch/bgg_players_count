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
        output.writelines(process_games(CLIGamesParser(argv[2:])))
    return 0


def process_games(games: Iterable[int]) -> Iterator[str]:
    index = 1
    for game_id in games:
        print(f"Processing plays for game {index:03d}: ID={game_id}")

        player_count_logic = PlayerCountAggregatorLogic()
        for play in RequestPlays(thingid=game_id).queryAll():
            player_count_logic.visit(play)

        yield f"{SEPARATOR.join(game_metadata(game_id))}{SEPARATOR}{PlayerCountAggregatorCSVPresenter(player_count_logic, SEPARATOR).render()}\n"

        index += 1

    print(f"Finished processing {index-1} games")


def game_metadata(game_id: int) -> List[str]:
    game = RequestThing(game_id).query().only_item()
    return [
        f"{game.id()}",
        game.primary_name(),
        game.type(),
        f"{game.year_published()}",
    ]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
