import datetime
import itertools
import xml.etree.ElementTree as ET
from typing import Dict, Generator, Iterable, Iterator, Optional, Sized

from ..model.Play import Play
from ..model.Plays import Plays
from ..utils import InlineOutput
from .RequestBase import RequestBase

# Each page in the API responses contains up to 100 entries.
ENTRIES_IN_FULL_PAGE = 100


class RequestPlays(RequestBase[Plays], Sized, Iterable[Plays]):
    """
    A request for a list of plays for the specific object.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc10
    """

    def __init__(self, username: Optional[str] = None, thingid: Optional[int] = None):
        if not username and not thingid:
            raise Exception("Either username or id required to query plays")
        self.__userName = username
        self.__id = thingid
        self.__type: Optional[str] = None
        self.__minDate: Optional[datetime.date] = None
        self.__maxDate: Optional[datetime.date] = None
        self.__subType: Optional[str] = None

    def filter_on(
        self,
        thingtype: Optional[str] = None,
        subtype: Optional[str] = None,
        mindate: Optional[datetime.date] = None,
        maxdate: Optional[datetime.date] = None,
    ) -> "RequestPlays":
        self.__type = thingtype
        self.__minDate = mindate
        self.__maxDate = maxdate
        self.__subType = subtype
        return self

    def queryAll(self) -> Generator[Play, None, None]:
        for plays in self:
            for play in plays:
                yield play

    def __iter__(self) -> Iterator[Plays]:
        total = None
        for page in itertools.count(start=1):
            InlineOutput.overwrite(f"Fetching page {page}")
            if total:
                InlineOutput.write(f" of {total} ({100*(page/total):.2f})")
            plays = self._fetch(page=page)

            if not total:
                total = (plays.total() // ENTRIES_IN_FULL_PAGE) + 1

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
        return self._fetch().total()

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "plays"

    def _api_params(self, **kwargs) -> Dict[str, str]:
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

        params["page"] = str(kwargs["page"])

        return params

    def _build_response(self, root: ET.Element) -> Plays:
        return Plays(root)

    def _cache_dir(self) -> Optional[str]:
        return f"{self.__id}"

    def _cache_file_name(str, **kwargs) -> str:
        return f"{kwargs['page']:04d}"
