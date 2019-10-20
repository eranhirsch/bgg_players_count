import xml.etree.ElementTree as ET
from typing import List

from utils import nullthrows

from .Play import Play


class BGGPlaysList:
    __total: int
    __page: int
    __plays: List[Play]

    @staticmethod
    def fromElementTree(root: ET.Element) -> "BGGPlaysList":
        if root.tag != "plays":
            raise Exception(f"Unexpected root tag: {root.tag}")

        plays = BGGPlaysList()
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
        return f"BGGPlaysList/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self.plays())}"
