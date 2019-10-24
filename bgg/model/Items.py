import xml.etree.ElementTree as ET
from typing import Iterable, Iterator, Sized

from ..utils import nonthrows
from .SearchItem import SearchItem


class Items(Sized, Iterable[SearchItem]):
    __total: int
    __root: ET.Element

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Items":
        if root.tag != "items":
            raise Exception(f"Unexpected root tag: {root.tag}")

        items = Items()
        items.__total = int(nonthrows(root.get("total")))
        items.__root = root
        return items

    def total(self) -> int:
        return self.__total

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
