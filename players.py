#!/usr/local/bin/python3

import sys

from bgg.api.RequestPlays import RequestPlays


def main(argv=[]) -> int:
    if len(argv) > 1:
        id = int(argv[1])
    else:
        id = 63888  # Innovation
        count = 0
        for play in RequestPlays().forID(id).queryAll():
            print(play)
            count += 1
            if count >= 10:
                break

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
