import xml.etree.ElementTree as ET
from typing import Optional

from ..utils import nonthrows
from .ModelBase import ModelBase


class Player(ModelBase):
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "player":
            raise Exception(f"Unexpected root tag: {root.tag}")
        self.__root = root

    def userName(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self.__root.get("username")))

    def userID(self) -> Optional[int]:
        return Player._nonifyInt(nonthrows(self.__root.get("userid")))

    def name(self) -> str:
        return nonthrows(self.__root.get("name"))

    def startPosition(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self.__root.get("startposition")))

    def color(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self.__root.get("color")))

    def score(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self.__root.get("score")))

    def isNew(self) -> bool:
        return Player._stringToBool(nonthrows(self.__root.get("new")))

    def rating(self) -> float:
        return float(nonthrows(self.__root.get("rating")))

    def isWinner(self) -> bool:
        return Player._stringToBool(nonthrows(self.__root.get("win")))
