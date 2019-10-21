import datetime
import xml.etree.ElementTree as ET
from typing import List, Optional

from ..utils import nonthrows
from .Item import Item
from .ModelBase import ModelBase
from .Player import Player


class Play(ModelBase):
    __id: int
    __userID: int
    __date: datetime.date
    __quantity: int
    __length: datetime.timedelta
    __incomplete: bool
    __nowinstats: bool
    __location: str
    __item: Item
    __comments: Optional[str] = None
    __players: Optional[List[Player]] = None

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Play":
        if root.tag != "play":
            raise Exception(f"Unexpected root tag: {root.tag}")

        play = Play()
        play.__id = int(nonthrows(root.get("id")))
        play.__userID = int(nonthrows(root.get("userid")))
        play.__date = datetime.date.fromisoformat(nonthrows(root.get("date")))
        play.__quantity = int(nonthrows(root.get("quantity")))
        play.__length = datetime.timedelta(seconds=int(nonthrows(root.get("length"))))
        play.__incomplete = Play._stringToBool(nonthrows(root.get("incomplete")))
        play.__nowinstats = Play._stringToBool(nonthrows(root.get("nowinstats")))
        play.__location = nonthrows(root.get("location"))
        play.__item = Item.fromElementTree(nonthrows(root.find("item")))

        comments = root.find("comments")
        if comments:
            play.__comments = comments.text

        players = root.find("players")
        if players:
            play.__players = [
                Player.fromElementTree(player) for player in list(players)
            ]

        return play

    def id(self) -> int:
        return self.__id

    def userID(self) -> int:
        return self.__userID

    def date(self) -> datetime.date:
        return self.__date

    def quantity(self) -> int:
        return self.__quantity

    def length(self) -> datetime.timedelta:
        return self.__length

    def is_incomplete(self) -> bool:
        return self.__incomplete

    def is_nowinstats(self) -> bool:
        return self.__nowinstats

    def location(self) -> str:
        return self.__location

    def item(self) -> Item:
        return self.__item

    def comments(self) -> Optional[str]:
        return self.__comments

    def players(self) -> Optional[List[Player]]:
        return self.__players

    def __str__(self) -> str:
        return f"Play/ID: {self.id()}, UserID: {self.userID()}, Date: {self.date()}, Quantity: {self.quantity()}, Length: {self.length()}, IsIncomplete: {self.is_incomplete()}, NoWinStats: {self.is_nowinstats()}, Location: {self.location()}, Item: {self.item()}"
