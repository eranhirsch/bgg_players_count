import xml.etree.ElementTree as ET
from typing import List

from bgg.api.BGGPlaysRequest import *
from bgg.model.BGGPlay import *
from utils import nullthrows


class BGGPlaysList:
    __total: int
    __page: int
    __plays: List[BGGPlay]
    __originRequest: "BGGPlaysRequest"

    @staticmethod
    def fromElementTree(root: ET.Element, request: "BGGPlaysRequest") -> "BGGPlaysList":
        if root.tag != "plays":
            raise Exception(f"Unexpected root tag: {root.tag}")

        plays = BGGPlaysList()
        plays.__total = int(nullthrows(root.get("total")))
        plays.__page = int(nullthrows(root.get("page")))
        plays.__plays = [BGGPlay.fromElementTree(child) for child in root]
        plays.__originRequest = request
        return plays

    def total(self) -> int:
        return self.__total

    def page(self) -> int:
        return self.__page

    def originRequest(self) -> "BGGPlaysRequest":
        return self.__originRequest

    def plays(self) -> List[BGGPlay]:
        return self.__plays

    def __str__(self) -> str:
        return f"BGGPlaysList/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self.plays())}, Origin: {self.originRequest()}"
