import xml.etree.ElementTree as ET
from typing import Iterable, Iterator, Sized

from ..utils import nonthrows
from .SearchItem import SearchItem


class Items(Sized, Iterable[SearchItem]):
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "items":
            raise Exception(f"Unexpected root tag: {root.tag}")

        self.__root = root

    def total(self) -> int:
        return int(nonthrows(self.__root.get("total")))

    def __len__(self) -> int:
        return len(self.__root)

    def __iter__(self) -> Iterator[SearchItem]:
        for child in self.__root:
            try:
                yield SearchItem(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise
