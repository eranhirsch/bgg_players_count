#!/usr/local/bin/python3

import sys

from bgg.api.RequestPlays import RequestPlays


def main(argv=[]) -> int:
    # Fallback to Innovation for now...
    id = int(argv[1]) if len(argv) > 1 else 63888
    print(f"Processing plays for: ID={id}")
    for play in RequestPlays().forID(id).queryAll():
        print(play)

    print(f"Finished processing")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
