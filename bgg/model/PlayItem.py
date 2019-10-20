import xml.etree.ElementTree as ET
from typing import List

from utils import nullthrows


class PlayItem:
    __name: str
    __objectType: str
    __objectID: int
    __subTypes: List[str]

    @staticmethod
    def fromElementTree(root: ET.Element) -> "PlayItem":
        if root.tag != "item":
            raise Exception(f"Unexpected root tag: {root.tag}")

        item = PlayItem()
        item.__name = nullthrows(root.get("name"))
        item.__objectType = nullthrows(root.get("objecttype"))
        item.__objectID = int(nullthrows(root.get("objectid")))
        item.__subTypes = [
            nullthrows(subtype.get("value"))
            for subtype in list(nullthrows(root.find("subtypes")))
        ]
        return item

    def name(self) -> str:
        return self.__name

    def objectType(self) -> str:
        return self.__objectType

    def objectID(self) -> int:
        return self.__objectID

    def subTypes(self) -> List[str]:
        return self.__subTypes

    def __str__(self) -> str:
        return f"PlayItem/Name: {self.name()}, Type: {self.objectType()}, ID: {self.objectID()}, Subtypes: {':'.join(self.subTypes())}"
