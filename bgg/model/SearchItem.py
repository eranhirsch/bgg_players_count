import xml.etree.ElementTree as ET
from typing import Tuple

from ..utils import nonthrows


class SearchItem:
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "item":
            raise Exception(f"Unexpected root tag: {root.tag}")

        self.__root = root

    def type(self) -> str:
        return nonthrows(self.__root.get("type"))

    def id(self) -> int:
        return int(nonthrows(self.__root.get("id")))

    def name(self) -> Tuple[str, str]:
        name_elem = nonthrows(self.__root.find("name"))
        return (nonthrows(name_elem.get("value")), nonthrows(name_elem.get("type")))

    def yearPublished(self) -> int:
        return int(nonthrows(nonthrows(self.__root.find("yearpublished")).get("value")))
