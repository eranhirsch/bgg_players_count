#!/usr/local/bin/python3

import sys

from bgg.api.RequestList import RequestList


def main(argv=[]) -> int:
    listid = int(argv[1])

    items = RequestList(listid).fetch().items()
    if not items:
        return 1

    for item in items:
        print(
            f"{item.edit_date()}, {item.id()}, {item.image_id()}, {item.object_id()}, {item.object_name()}, {item.object_type()}, {item.post_date()}, {item.sub_type()}, {item.thumbs()}, {item.user_name()}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
