#!/usr/local/bin/python3

import sys

from bgg.api.RequestList import RequestList
from bgg.api.RequestPlays import RequestPlays


def main(argv=[]) -> int:
    listid = int(argv[1])

    geeklist = RequestList(listid).fetch()

    print(
        f'Caching geeklist "{geeklist.title()}" by {geeklist.user_name()} [last updated: {geeklist.edit_date()}]'
    )

    for item in geeklist.items():
        if item.object_type() != "thing":
            print(
                f"Skipping: {item.object_name()} ({item.object_id()})/Wrong type: '{item.object_type()}'"
            )
            continue

        if item.sub_type() != "boardgame":
            print(
                f"Skipping: {item.object_name()} ({item.object_id()})/Wrong subtype: '{item.sub_type()}'"
            )
            continue

        print(
            f"Caching item {item.object_id()}: {item.object_name()} ({item.object_id()})"
        )
        for play in RequestPlays(thingid=item.object_id()):
            pass  # we just want to iterate over the plays
        print("\nDone!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
