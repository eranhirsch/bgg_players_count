import xml.etree.ElementTree as ET
from typing import List

from ..utils import nonthrows


class PlayItem:
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "item":
            raise Exception(f"Unexpected root tag: {root.tag}")
        self.__root = root

    def name(self) -> str:
        return nonthrows(self.__root.get("name"))

    def objectType(self) -> str:
        return nonthrows(self.__root.get("objecttype"))

    def objectID(self) -> int:
        return int(nonthrows(self.__root.get("objectid")))

    def subTypes(self) -> List[str]:
        return [
            nonthrows(subtype.get("value"))
            for subtype in list(nonthrows(self.__root.find("subtypes")))
        ]

    def __str__(self) -> str:
        return f"PlayItem/Name: {self.name()}, Type: {self.objectType()}, ID: {self.objectID()}, Subtypes: {':'.join(self.subTypes())}"
