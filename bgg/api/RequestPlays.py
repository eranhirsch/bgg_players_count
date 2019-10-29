import datetime
import itertools
import os
import tempfile
import time
import xml.etree.ElementTree as ET
from typing import Dict, Generator, Iterable, Iterator, Optional, Sized

import requests

from ..model.Play import Play
from ..model.Plays import Plays
from ..utils import nonthrows

BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"

# Each page in the API responses contains up to 100 entries.
ENTRIES_IN_FULL_PAGE = 100

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429

MAX_RETRIES = 5


class RequestPlays(Sized, Iterable[Plays]):
    """
    A request for a list of plays for the specific object.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc10
    """

    def __init__(
        self,
        username: Optional[str] = None,
        thingid: Optional[int] = None,
        thingtype: Optional[str] = None,
        subtype: Optional[str] = None,
        mindate: Optional[datetime.date] = None,
        maxdate: Optional[datetime.date] = None,
    ):
        if not username and not thingid:
            raise Exception("Either username or id required to query plays")

        self.__userName = username
        self.__id = thingid
        self.__type = thingtype
        self.__minDate = mindate
        self.__maxDate = maxdate
        self.__subType = subtype

    def querySinglePage(self, page: int = 0) -> Plays:
        uri = f"{BASE_URL}plays"
        params = self.__getParams()
        params["page"] = str(page)

        for retries in range(MAX_RETRIES):
            response = requests.get(uri, params=params)
            response_text = response.text
            self.__cacheResponse(response_text, page)
            root = ET.fromstring(response_text)

            if response.status_code == HTTP_STATUS_CODE_OK:
                print(f"Page {page} received")
                return Plays(root)

            elif response.status_code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS:
                if root.tag != "error":
                    raise Exception(
                        f"Unexpected error format, was exepecting 'error' tag but got {root.tag}"
                    )
                message = nonthrows(root.find("message")).text
                retry_secs = 2 ** (retries)  # Exponential backoff
                print(f'TOO MANY REQUESTS["{message}"]. Retrying in {retry_secs}s')
                time.sleep(retry_secs)

            else:
                raise Exception(f"Bad API response: {response.status_code}")

        raise Exception(
            f"Bailing out! failed to query server for page {page} after {retries} retries"
        )

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

    def __len__(self) -> int:
        # Just use any really large number here which is unlikely to have entries in it
        empty_page = self.querySinglePage(9999)
        if len(empty_page) > 0:
            raise Exception(
                f"Unexpected error: Page {empty_page.page()} contained entries"
            )
        return empty_page.total()

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

    def __cacheResponse(self, response: str, page: int) -> None:
        cache_dir = f"{tempfile.gettempdir()}/bggcache/plays/{self.__id}"
        os.makedirs(cache_dir, exist_ok=True)
        with open(f"{cache_dir}/{page}.xml", "w") as cache:
            cache.write(response)
