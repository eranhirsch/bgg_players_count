import datetime
from typing import Iterable, Iterator, List, Optional, Sequence, Sized

from ..utils import LazySequence, nonthrows
from .ModelBase import ModelBase

# Some entries have their date set as this, we'll just assume it's missing for those cases
MISSING_DATE_VALUE = "0000-00-00"


class Player(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "player"

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


class Item(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "plays"

    def name(self) -> str:
        return self._field("name")

    def objectType(self) -> str:
        return self._field("objecttype")

    def objectID(self) -> int:
        return int(self._field("objectid"))

    def subTypes(self) -> List[str]:
        return [nonthrows(subtype.get("value")) for subtype in self._child("subtypes")]


class Play(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "play"

    def id(self) -> int:
        return int(self._field("id"))

    def userID(self) -> int:
        return int(self._field("userid"))

    def date(self) -> Optional[datetime.date]:
        try:
            return datetime.date.fromisoformat(self._field("date"))
        except ValueError:
            # Value errors mean the string was malformed
            return None

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

    def item(self) -> Item:
        return Item(nonthrows(self._root.find("item")))

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


class Page(ModelBase, Sized, Iterable[Play]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "plays"

    def total(self) -> int:
        return int(self._field("total"))

    def page(self) -> int:
        return int(self._field("page"))

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[Play]:
        for child in self._root:
            try:
                yield Play(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise
