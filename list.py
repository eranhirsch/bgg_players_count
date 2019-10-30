#!/usr/local/bin/python3

import sys

from bgg.api.RequestList import RequestList


def main(argv=[]) -> int:
    listid = int(argv[1])

    items = RequestList(listid).fetch().items()
    if not items:
        return 1

    for item in items:
        print(f"{item}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
