import xml.etree.ElementTree as ET
from typing import Iterable, Iterator, Sized

from ..utils import nonthrows
from .Play import Play


class Plays(Sized, Iterable[Play]):
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "plays":
            raise Exception(f"Unexpected root tag: {root.tag}")

        self.__root = root

    def total(self) -> int:
        return int(nonthrows(self.__root.get("total")))

    def page(self) -> int:
        return int(nonthrows(self.__root.get("page")))

    def __len__(self) -> int:
        return len(self.__root)

    def __iter__(self) -> Iterator[Play]:
        for child in self.__root:
            try:
                yield Play.fromElementTree(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise

    def __str__(self) -> str:
        return f"Plays/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self)}"
