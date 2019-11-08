#!/usr/local/bin/python3

import sys
from typing import Iterable, Iterator, List

from bgg.api.RequestPlays import RequestPlays
from CLIGamesParser import CLIGamesParser
from observers.PlayerCountAggregatorLogic import (
    PlayerCountAggregatorCSVPresenter,
    PlayerCountAggregatorLogic,
)


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

        yield f"{game_id}\t{PlayerCountAggregatorCSVPresenter(player_count_logic).render()}\n"

        index += 1

    print(f"Finished processing {index-1} games")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
