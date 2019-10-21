import xml.etree.ElementTree as ET
from typing import Optional

from ..utils import nonthrows
from .ModelBase import ModelBase


class Player(ModelBase):
    __userName: Optional[str]
    __userID: Optional[int]
    __name: str
    __startPosition: Optional[str]
    __color: Optional[str]
    __score: Optional[str]
    __isNew: bool
    __rating: float
    __isWinner: bool

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Player":
        if root.tag != "player":
            raise Exception(f"Unexpected root tag: {root.tag}")

        player = Player()
        player.__userName = Player.__nonifyStr(nonthrows(root.get("username")))
        player.__userID = Player.__nonifyInt(nonthrows(root.get("userid")))
        player.__name = nonthrows(root.get("name"))
        player.__startPosition = Player.__nonifyStr(
            nonthrows(root.get("startposition"))
        )
        player.__color = Player.__nonifyStr(nonthrows(root.get("color")))
        player.__score = Player.__nonifyStr(nonthrows(root.get("score")))
        player.__isNew = Player._stringToBool(nonthrows(root.get("new")))
        player.__rating = float(nonthrows(root.get("rating")))
        player.__isWinner = Player._stringToBool(nonthrows(root.get("win")))

        return player

    def userName(self) -> Optional[str]:
        return self.__userName

    def userID(self) -> Optional[int]:
        return self.__userID

    def name(self) -> str:
        return self.__name

    def startPosition(self) -> Optional[str]:
        return self.__startPosition

    def color(self) -> Optional[str]:
        return self.__color

    def score(self) -> Optional[str]:
        return self.__score

    def isNew(self) -> bool:
        return self.__isNew

    def rating(self) -> float:
        return self.__rating

    def isWinner(self) -> bool:
        return self.__isWinner

    @staticmethod
    def __nonifyStr(x: str) -> Optional[str]:
        return None if x == "" else x

    @staticmethod
    def __nonifyInt(x: str) -> Optional[int]:
        return None if x == "" or x == "0" else int(x)
