import xml.etree.ElementTree as ET
from typing import Optional

from utils import nullthrows


class Player:
    __userName: Optional[str]
    __userID: Optional[int]
    __name: str
    # __startPosition: Optional[int]
    # __color: Optional[str]
    # __score: Optional[int]
    # __new: bool
    # __rating: int
    # __didWin: bool

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Player":
        if root.tag != "player":
            raise Exception(f"Unexpected root tag: {root.tag}")

        player = Player()
        player.__userName = Player.__nonifyStr(nullthrows(root.get("username")))
        player.__userID = Player.__nonifyInt(int(nullthrows(root.get("userid"))))
        player.__name = nullthrows(root.get("name"))

        return player

    @staticmethod
    def __nonifyStr(x: str) -> Optional[str]:
        return None if x == "" else x

    @staticmethod
    def __nonifyInt(x: int) -> Optional[int]:
        return None if x == 0 else x
