import xml.etree.ElementTree as ET
from typing import Dict, Iterable, Iterator

from ..model.GeekList import GeekList
from ..model.GeekListItem import GeekListItem
from .RequestBase import RequestBase


class RequestList(RequestBase[GeekList], Iterable[GeekListItem]):
    """
    A request for a geek list of items
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API#toc7
    """

    def __init__(self, listid: int) -> None:
        self.__listID = listid

    def fetch(self, with_comments: bool = False) -> GeekList:
        return self._fetch(listid=self.__listID, with_comments=with_comments)

    def _api_version(self) -> int:
        return 1

    def _api_path(self, **kwargs) -> str:
        return f"geeklist/{kwargs['listid']}"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {}

        if kwargs["with_comments"]:
            params["comments"] = "1"

        return params

    def _build_response(self, root: ET.Element) -> GeekList:
        return GeekList(root)

    def _cache_file_name(str, **kwargs) -> str:
        return kwargs["listid"]

    def __iter__(self) -> Iterator[GeekListItem]:
        for item in self.fetch():
            yield item
