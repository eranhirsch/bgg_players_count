#!/usr/local/bin/python3

import sys

from bgg.api.RequestList import RequestList


def main(argv=[]) -> int:
    listid = int(argv[1])
    geeklist = RequestList(listid).query()
    print(
        f"Geeklist {geeklist.description()}, {geeklist.edit_date()}, {geeklist.id()}, {geeklist.post_date()}, {geeklist.thumbs()}, {geeklist.title()}, {geeklist.user_name()}, {len(geeklist)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
