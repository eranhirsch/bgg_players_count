import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Generator, Optional

import requests

from ..model.Play import Play
from ..model.PlaysList import PlaysList

BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"


class RequestPlays:
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

    def querySinglePage(self, page: int = 0) -> PlaysList:
        uri = f"{BASE_URL}plays"
        params = self.__getParams()
        params["page"] = str(page)
        response = requests.get(uri, params=params)

        if response.status_code != 200:
            raise Exception(f"Bad API response: {response.status_code}")

        root = ET.fromstring(response.text)
        playsList = PlaysList.fromElementTree(root)
        return playsList

    def queryAll(self) -> Generator[Play, None, None]:
        page = 0
        current_list = self.querySinglePage(page)
        while len(current_list.plays()) == 100:
            for play in current_list.plays():
                yield play
            page += 1
            current_list = self.querySinglePage(page)

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
