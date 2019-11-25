import xml.etree.ElementTree as ET
from typing import Dict, Optional

from ..model import Items, search
from .RequestBase import RequestItemsBase


class RequestSearch(RequestItemsBase[search.Item]):
    """
    A request for a list of items resulting from searching
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc14
    """

    def __init__(self) -> None:
        self.__type: Optional[str] = None

    def ofType(self, type: str) -> "RequestSearch":
        self.__type = type
        return self

    def query(self, query: str, is_exact: bool = True) -> Items[search.Item]:
        return self._fetch(query=query, is_exact=is_exact)

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "search"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {}

        if self.__type:
            params["type"] = self.__type

        params["query"] = kwargs["query"]
        if kwargs["is_exact"]:
            params["exact"] = "1"

        return params

    def _build_item(self, item_elem: ET.Element) -> search.Item:
        return search.Item(item_elem)

    def _cache_file_name(str, **kwargs) -> str:
        return kwargs["query"]
