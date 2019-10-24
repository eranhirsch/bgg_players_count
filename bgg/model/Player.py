from typing import Optional

from ..utils import nonthrows
from .ModelBase import ModelBase


class Player(ModelBase):
    def rootTagName(self) -> str:
        return "player"

    def userName(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self._root.get("username")))

    def userID(self) -> Optional[int]:
        return Player._nonifyInt(nonthrows(self._root.get("userid")))

    def name(self) -> str:
        return nonthrows(self._root.get("name"))

    def startPosition(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self._root.get("startposition")))

    def color(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self._root.get("color")))

    def score(self) -> Optional[str]:
        return Player._nonifyStr(nonthrows(self._root.get("score")))

    def isNew(self) -> bool:
        return Player._stringToBool(nonthrows(self._root.get("new")))

    def rating(self) -> float:
        return float(nonthrows(self._root.get("rating")))

    def isWinner(self) -> bool:
        return Player._stringToBool(nonthrows(self._root.get("win")))
