#!/usr/local/bin/python3

import sys
from typing import Dict

from bgg.api.RequestPlays import RequestPlays


def main(argv=[]) -> int:
    # Fallback to Innovation for now...
    id = int(argv[1]) if len(argv) > 1 else 63888
    print(f"Processing plays for: ID={id}")

    count = 0
    player_count_aggr: Dict[str, int] = {}
    try:
        for play in RequestPlays().forID(id).queryAll():
            players = play.players()
            player_count = f"{len(players)} Players" if players else "Missing"
            try:
                player_count_aggr[player_count] += 1
            except KeyError:
                player_count_aggr[player_count] = 1
            count += 1
            # if count >= 5000:
            #     break
        return 0
    except Exception:
        print(f"Encountered exception while processing")
        raise
    finally:
        print(f"Player Count: {player_count_aggr}")

    print(f"Finished processing")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
