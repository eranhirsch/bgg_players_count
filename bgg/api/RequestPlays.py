import datetime
import itertools
import xml.etree.ElementTree as ET
from typing import Dict, Generator, Iterable, Iterator, Optional, Sized, Tuple

from ..model import play
from ..utils import InlineOutput
from .RequestBase import RequestBase

# Each page in the API responses contains up to 100 entries.
ENTRIES_IN_FULL_PAGE = 100


class RequestPlays(RequestBase[play.Page], Sized, Iterable[play.Page]):
    """
    A request for a list of plays for the specific object.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc10
    """

    def __init__(
        self, username: Optional[str] = None, thingid: Optional[int] = None
    ) -> None:
        if not username and not thingid:
            raise Exception("Either username or id required to query plays")
        self.__user_name = username
        self.__id = thingid
        self.__type: Tuple[Optional[str], Optional[str]] = (None, None)
        self.__date: Tuple[Optional[datetime.date], Optional[datetime.date]] = (
            None,
            None,
        )

    def filter_on(
        self,
        type: Tuple[Optional[str], Optional[str]] = (None, None),
        date: Tuple[Optional[datetime.date], Optional[datetime.date]] = (None, None),
    ) -> "RequestPlays":
        self.__type = type
        self.__date = date
        return self

    def queryAll(self) -> Generator[play.Play, None, None]:
        for plays in self:
            for p in plays:
                yield p

    def __iter__(self) -> Iterator[play.Page]:
        total = None
        for page in itertools.count(start=1):
            InlineOutput.overwrite(f"Fetching page {page}")
            if total:
                InlineOutput.write(f" of {total} ({100*(page/total):.2f}%)")
            plays = self._fetch(page=page)

            if not total:
                total = (plays.total() // ENTRIES_IN_FULL_PAGE) + 1

            if plays:
                yield plays
            else:
                InlineOutput.write(" Empty page fetched!")

            if len(plays) < ENTRIES_IN_FULL_PAGE:
                # We can guess when the generation is done if the number of
                # plays we got is lower than the usual number in a full page
                InlineOutput.write(" DONE!\n")
                return "Last page received"

    def __len__(self) -> int:
        return self._fetch().total()

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "plays"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {}

        if self.__user_name:
            params["username"] = self.__user_name

        if self.__id:
            params["id"] = f"{self.__id}"

        type = self.__type[0]
        if type:
            params["type"] = type

        sub_type = self.__type[1]
        if sub_type:
            params["subtype"] = sub_type

        min_date = self.__date[0]
        if min_date:
            params["mindate"] = f"{min_date}"

        max_date = self.__date[1]
        if max_date:
            params["maxdate"] = f"{max_date}"

        params["page"] = f'{kwargs["page"]}'

        return params

    def _build_response(self, root: ET.Element, **kwargs) -> play.Page:
        return play.Page(root)

    def _cache_dir(self) -> Optional[str]:
        return f"{self.__id}" if self.__id else f"user_{self.__user_name}"

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        if self.__type[0] or self.__type[1] or self.__date[0] or self.__date[1]:
            # Dont cache filtered queries atm
            return None

        return f"{kwargs['page']:04d}"
