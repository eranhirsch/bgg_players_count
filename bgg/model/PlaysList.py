import xml.etree.ElementTree as ET
from typing import List

from utils import nullthrows

from .Play import Play


class PlaysList:
    __total: int
    __page: int
    __plays: List[Play]

    @staticmethod
    def fromElementTree(root: ET.Element) -> "PlaysList":
        if root.tag != "plays":
            raise Exception(f"Unexpected root tag: {root.tag}")

        plays = PlaysList()
        plays.__total = int(nullthrows(root.get("total")))
        plays.__page = int(nullthrows(root.get("page")))
        plays.__plays = [Play.fromElementTree(child) for child in root]
        return plays

    def total(self) -> int:
        return self.__total

    def page(self) -> int:
        return self.__page

    def plays(self) -> List[Play]:
        return self.__plays

    def __str__(self) -> str:
        return f"PlaysList/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self.plays())}"
