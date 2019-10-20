import xml.etree.ElementTree as ET

from utils import nullthrows


class PlayItem:
    __name: str
    __objectType: str
    __objectID: int

    @staticmethod
    def fromElementTree(root: ET.Element) -> "PlayItem":
        if root.tag != "item":
            raise Exception(f"Unexpected root tag: {root.tag}")

        item = PlayItem()
        item.__name = nullthrows(root.get("name"))
        item.__objectType = nullthrows(root.get("objecttype"))
        item.__objectID = int(nullthrows(root.get("objectid")))
        return item

    def name(self) -> str:
        return self.__name

    def objectType(self) -> str:
        return self.__objectType

    def objectID(self) -> int:
        return self.__objectID
