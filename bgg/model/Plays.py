import xml.etree.ElementTree as ET
from typing import Iterable, Iterator, Sized

from utils import nullthrows

from .Play import Play


class Plays(Sized, Iterable[Play]):
    __total: int
    __page: int
    __root: ET.Element

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Plays":
        if root.tag != "plays":
            raise Exception(f"Unexpected root tag: {root.tag}")

        plays = Plays()
        plays.__total = int(nullthrows(root.get("total")))
        plays.__page = int(nullthrows(root.get("page")))
        plays.__root = root
        return plays

    def total(self) -> int:
        return self.__total

    def page(self) -> int:
        return self.__page

    def __len__(self) -> int:
        return len(self.__root)

    def __iter__(self) -> Iterator[Play]:
        for child in self.__root:
            yield Play.fromElementTree(child)

    def __str__(self) -> str:
        return f"Plays/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self)}"
