import xml.etree.ElementTree as ET
from typing import Dict

from ..model import geeklist
from .RequestBase import RequestBase


class RequestList(RequestBase[geeklist.List]):
    """
    A request for a geek list of items
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API#toc7
    """

    def __init__(self, listid: int) -> None:
        self.__listID = listid

    def fetch(self, with_comments: bool = False) -> geeklist.List:
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

    def _build_response(self, root: ET.Element, **kwargs) -> geeklist.List:
        return geeklist.List(root)

    def _cache_file_name(str, **kwargs) -> str:
        return kwargs["listid"]
