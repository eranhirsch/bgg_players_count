import xml.etree.ElementTree as ET
from typing import Optional

from utils import nullthrows

from .ModelBase import ModelBase


class Player(ModelBase):
    __userName: Optional[str]
    __userID: Optional[int]
    __name: str
    __startPosition: Optional[str]
    __color: Optional[str]
    __score: Optional[str]
    __isNew: bool
    __rating: int
    __isWinner: bool

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Player":
        if root.tag != "player":
            raise Exception(f"Unexpected root tag: {root.tag}")

        player = Player()
        player.__userName = Player.__nonifyStr(nullthrows(root.get("username")))
        player.__userID = Player.__nonifyInt(nullthrows(root.get("userid")))
        player.__name = nullthrows(root.get("name"))
        player.__startPosition = Player.__nonifyStr(
            nullthrows(root.get("startposition"))
        )
        player.__color = Player.__nonifyStr(nullthrows(root.get("color")))
        player.__score = Player.__nonifyStr(nullthrows(root.get("score")))
        player.__isNew = Player._stringToBool(nullthrows(root.get("new")))
        player.__rating = int(nullthrows(root.get("rating")))
        player.__isWinner = Player._stringToBool(nullthrows(root.get("win")))

        return player

    @staticmethod
    def __nonifyStr(x: str) -> Optional[str]:
        return None if x == "" else x

    @staticmethod
    def __nonifyInt(x: str) -> Optional[int]:
        return None if x == "" or x == "0" else int(x)
