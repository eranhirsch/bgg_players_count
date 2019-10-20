import datetime
import itertools
import xml.etree.ElementTree as ET
from typing import Dict, Generator, Iterable, Iterator, Optional

import requests

from ..model.Play import Play
from ..model.Plays import Plays

BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"

# Each page in the API responses contains up to 100 entries. This isn't
# documented anywhere though, so it might be incorrect in some cases, or simply
# change in the future.
ENTRIES_IN_FULL_PAGE = 100


class RequestPlays(Iterable[Plays]):
    """
    A request for a list of plays for the specific object.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc10
    """

    __userName: Optional[str]
    __id: Optional[int]
    __type: Optional[str]
    __minDate: Optional[datetime.date]
    __maxDate: Optional[datetime.date]
    __subType: Optional[str]

    def __init__(self):
        self.__userName = None
        self.__id = None
        self.__type = None
        self.__minDate = None
        self.__maxDate = None
        self.__subType = None

    def forUserName(self, userName: str) -> "RequestPlays":
        self.__userName = userName
        return self

    def forID(self, id: int) -> "RequestPlays":
        self.__id = id
        return self

    def ofType(self, type: str) -> "RequestPlays":
        self.__type = type
        return self

    def fromDate(self, minDate: datetime.date) -> "RequestPlays":
        self.__minDate = minDate
        return self

    def toDate(self, maxDate: datetime.date) -> "RequestPlays":
        self.__maxDate = maxDate
        return self

    def ofSubType(self, subType: str) -> "RequestPlays":
        self.__subType = subType
        return self

    def querySinglePage(self, page: int = 0) -> Plays:
        uri = f"{BASE_URL}plays"
        params = self.__getParams()
        params["page"] = str(page)
        response = requests.get(uri, params=params)

        if response.status_code != 200:
            raise Exception(f"Bad API response: {response.status_code}")

        root = ET.fromstring(response.text)
        plays = Plays.fromElementTree(root)
        return plays

    def queryAll(self) -> Generator[Play, None, None]:
        for plays in self:
            for play in plays:
                yield play

    def __iter__(self) -> Iterator[Plays]:
        for page in itertools.count(start=1):
            plays = self.querySinglePage(page)

            if plays:
                yield plays
            else:
                # Response returned no plays
                break

            if len(plays) < ENTRIES_IN_FULL_PAGE:
                # We can guess when the generation is done if the number of
                # plays we got is lower than the usual number in a full page
                break

    def __getParams(self) -> Dict[str, str]:
        params = {}

        if self.__userName:
            params["username"] = self.__userName

        if self.__id:
            params["id"] = str(self.__id)

        if self.__type:
            params["type"] = self.__type

        if self.__minDate:
            params["mindate"] = str(self.__minDate)

        if self.__maxDate:
            params["maxdate"] = str(self.__maxDate)

        if self.__subType:
            params["subtype"] = self.__subType

        return params
