import datetime
import xml.etree.ElementTree as ET
from typing import List, Optional

from ..utils import nonthrows
from .ModelBase import ModelBase
from .Player import Player
from .PlayItem import PlayItem


class Play(ModelBase):
    def __init__(self, root: ET.Element) -> None:
        if root.tag != "play":
            raise Exception(f"Unexpected root tag: {root.tag}")
        self.__root = root

    def id(self) -> int:
        return int(nonthrows(self.__root.get("id")))

    def userID(self) -> int:
        return int(nonthrows(self.__root.get("userid")))

    def date(self) -> datetime.date:
        return datetime.date.fromisoformat(nonthrows(self.__root.get("date")))

    def quantity(self) -> int:
        return int(nonthrows(self.__root.get("quantity")))

    def length(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=int(nonthrows(self.__root.get("length"))))

    def is_incomplete(self) -> bool:
        return Play._stringToBool(nonthrows(self.__root.get("incomplete")))

    def is_nowinstats(self) -> bool:
        return Play._stringToBool(nonthrows(self.__root.get("nowinstats")))

    def location(self) -> Optional[str]:
        return Play._nonifyStr(nonthrows(self.__root.get("location")))

    def item(self) -> PlayItem:
        return PlayItem.fromElementTree(nonthrows(self.__root.find("item")))

    def comments(self) -> Optional[str]:
        comments = self.__root.find("comments")
        if not comments:
            return None
        return comments.text

    def players(self) -> Optional[List[Player]]:
        players = self.__root.find("players")
        if not players:
            return None
        return [Player.fromElementTree(player) for player in list(players)]

    def __str__(self) -> str:
        return f"Play/ID: {self.id()}, UserID: {self.userID()}, Date: {self.date()}, Quantity: {self.quantity()}, Length: {self.length()}, IsIncomplete: {self.is_incomplete()}, NoWinStats: {self.is_nowinstats()}, Location: {self.location()}, PlayItem: {self.item()}"
