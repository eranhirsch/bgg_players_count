import datetime
from typing import List, Optional

from ..utils import nonthrows
from .ModelBase import ModelBase
from .Player import Player
from .PlayItem import PlayItem


class Play(ModelBase):
    def rootTagName(self) -> str:
        return "play"

    def id(self) -> int:
        return int(self._fieldRaw("id"))

    def userID(self) -> int:
        return int(self._fieldRaw("userid"))

    def date(self) -> datetime.date:
        return datetime.date.fromisoformat(self._fieldRaw("date"))

    def quantity(self) -> int:
        return int(self._fieldRaw("quantity"))

    def length(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=int(self._fieldRaw("length")))

    def is_incomplete(self) -> bool:
        return Play._stringToBool(self._fieldRaw("incomplete"))

    def is_nowinstats(self) -> bool:
        return Play._stringToBool(self._fieldRaw("nowinstats"))

    def location(self) -> Optional[str]:
        return Play._nonifyStr(self._fieldRaw("location"))

    def item(self) -> PlayItem:
        return PlayItem(nonthrows(self._root.find("item")))

    def comments(self) -> Optional[str]:
        comments = self._root.find("comments")
        if not comments:
            return None
        return comments.text

    def players(self) -> Optional[List[Player]]:
        players = self._root.find("players")
        if not players:
            return None
        return [Player(player) for player in list(players)]

    def __str__(self) -> str:
        return f"Play/ID: {self.id()}, UserID: {self.userID()}, Date: {self.date()}, Quantity: {self.quantity()}, Length: {self.length()}, IsIncomplete: {self.is_incomplete()}, NoWinStats: {self.is_nowinstats()}, Location: {self.location()}, PlayItem: {self.item()}"
