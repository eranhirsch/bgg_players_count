#!/usr/local/bin/python3

import sys

from bgg.api.RequestList import RequestList


def main(argv=[]) -> int:
    listid = int(argv[1])
    geeklist = RequestList(listid).fetch()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
