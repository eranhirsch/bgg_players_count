import xml.etree.ElementTree as ET
from typing import Tuple

from ..utils import nonthrows


class SearchItem:
    __type: str
    __id: int
    __name: Tuple[str, str]
    __yearPublished: int

    @staticmethod
    def fromElementTree(root: ET.Element) -> "SearchItem":
        if root.tag != "item":
            raise Exception(f"Unexpected root tag: {root.tag}")

        item = SearchItem()
        item.__type = nonthrows(root.get("type"))
        item.__id = int(nonthrows(root.get("id")))
        name_elem = nonthrows(root.find("name"))
        item.__name = (
            nonthrows(name_elem.get("value")),
            nonthrows(name_elem.get("type")),
        )
        item.__yearPublished = int(
            nonthrows(nonthrows(root.find("yearpublished")).get("value"))
        )
        return item

    def type(self) -> str:
        return self.__type

    def id(self) -> int:
        return self.__id

    def name(self) -> Tuple[str, str]:
        return self.__name

    def yearPublished(self) -> int:
        return self.__yearPublished
