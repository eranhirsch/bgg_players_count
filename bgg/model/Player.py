from typing import Optional

from .ModelBase import ModelBase


class Player(ModelBase):
    def userName(self) -> Optional[str]:
        return Player._nonifyStr(self._field("username"))

    def userID(self) -> Optional[int]:
        return Player._nonifyInt(self._field("userid"))

    def name(self) -> str:
        return self._field("name")

    def startPosition(self) -> Optional[str]:
        return Player._nonifyStr(self._field("startposition"))

    def color(self) -> Optional[str]:
        return Player._nonifyStr(self._field("color"))

    def score(self) -> Optional[str]:
        return Player._nonifyStr(self._field("score"))

    def isNew(self) -> bool:
        return Player._stringToBool(self._field("new"))

    def rating(self) -> float:
        return float(self._field("rating"))

    def isWinner(self) -> bool:
        return Player._stringToBool(self._field("win"))

    def _rootTagName(self) -> str:
        return "player"
