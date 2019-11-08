import datetime
from typing import Optional, Sequence

from ..utils import LazySequence, nonthrows
from .ModelBase import ModelBase
from .Player import Player
from .PlayItem import PlayItem

# Some entries have their date set as this, we'll just assume it's missing for those cases
MISSING_DATE_VALUE = "0000-00-00"


class Play(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "play"

    def id(self) -> int:
        return int(self._field("id"))

    def userID(self) -> int:
        return int(self._field("userid"))

    def date(self) -> Optional[datetime.date]:
        date_str = self._field("date")
        if date_str == MISSING_DATE_VALUE:
            return None
        return datetime.date.fromisoformat(date_str)

    def quantity(self) -> int:
        return int(self._field("quantity"))

    def length(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=int(self._field("length")))

    def is_incomplete(self) -> bool:
        return Play._stringToBool(self._field("incomplete"))

    def is_nowinstats(self) -> bool:
        return Play._stringToBool(self._field("nowinstats"))

    def location(self) -> Optional[str]:
        return Play._nonifyStr(self._field("location"))

    def item(self) -> PlayItem:
        return PlayItem(nonthrows(self._root.find("item")))

    def comments(self) -> Optional[str]:
        comments = self._root.find("comments")
        if not comments:
            return None
        return comments.text

    def players(self) -> Optional[Sequence[Player]]:
        players = self._root.find("players")
        if not players:
            return None
        return LazySequence(players, lambda player: Player(player))
