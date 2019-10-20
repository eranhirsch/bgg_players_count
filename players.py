#!/usr/local/bin/python3

import sys
from typing import Dict

from bgg.api.RequestPlays import RequestPlays


def main(argv=[]) -> int:
    # Fallback to Innovation for now...
    id = int(argv[1]) if len(argv) > 1 else 63888
    print(f"Processing plays for: ID={id}")

    count = 0
    player_count: Dict[int, int] = {}
    for play in RequestPlays().forID(id).queryAll():
        players = play.players()
        if players:
            try:
                player_count[len(players)] += 1
            except KeyError:
                player_count[len(players)] = 1
        count += 1
        if count >= 5000:
            break

    print(f"Player Count: {player_count}")

    print(f"Finished processing")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
