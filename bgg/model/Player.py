from typing import Optional

from .ModelBase import ModelBase


class Player(ModelBase):
    def rootTagName(self) -> str:
        return "player"

    def userName(self) -> Optional[str]:
        return Player._nonifyStr(self._fieldRaw("username"))

    def userID(self) -> Optional[int]:
        return Player._nonifyInt(self._fieldRaw("userid"))

    def name(self) -> str:
        return self._fieldRaw("name")

    def startPosition(self) -> Optional[str]:
        return Player._nonifyStr(self._fieldRaw("startposition"))

    def color(self) -> Optional[str]:
        return Player._nonifyStr(self._fieldRaw("color"))

    def score(self) -> Optional[str]:
        return Player._nonifyStr(self._fieldRaw("score"))

    def isNew(self) -> bool:
        return Player._stringToBool(self._fieldRaw("new"))

    def rating(self) -> float:
        return float(self._fieldRaw("rating"))

    def isWinner(self) -> bool:
        return Player._stringToBool(self._fieldRaw("win"))
