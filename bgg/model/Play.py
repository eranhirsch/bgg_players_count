import datetime
import xml.etree.ElementTree as ET
from typing import List

from utils import nullthrows


class Play:
    __id: int
    __userID: int
    __date: datetime.date
    __quantity: int
    __length: datetime.timedelta
    __incomplete: bool
    __nowinstats: bool
    __location: str
    __items: List[ET.Element]

    @staticmethod
    def fromElementTree(root: ET.Element) -> "Play":
        if root.tag != "play":
            raise Exception(f"Unexpected root tag: {root.tag}")

        play = Play()
        play.__id = int(nullthrows(root.get("id")))
        play.__userID = int(nullthrows(root.get("userid")))
        play.__date = datetime.date.fromisoformat(nullthrows(root.get("date")))
        play.__quantity = int(nullthrows(root.get("quantity")))
        play.__length = datetime.timedelta(seconds=int(nullthrows(root.get("length"))))
        play.__incomplete = Play.__stringToBool(nullthrows(root.get("incomplete")))
        play.__nowinstats = Play.__stringToBool(nullthrows(root.get("nowinstats")))
        play.__location = nullthrows(root.get("location"))
        play.__items = list(root)
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

    def items(self) -> List[ET.Element]:
        return self.__items

    def __str__(self) -> str:
        return f"Play/ID: {self.id()}, UserID: {self.userID()}, Date: {self.date()}, Quantity: {self.quantity()}, Length: {self.length()}, IsIncomplete: {self.is_incomplete()}, NoWinStats: {self.is_nowinstats()}, Location: {self.location()}, Items: {len(self.items())}"

    @staticmethod
    def __stringToBool(str) -> bool:
        if str == "0":
            return False
        elif str == "1":
            return True
        else:
            raise Exception(f"Unexpected boolean value {str}")
