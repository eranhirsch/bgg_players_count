import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence

from ..model.ThingItems import ThingItems
from ..utils import firstx
from .RequestBase import RequestBase


class RequestThing(RequestBase):
    """
    A request for a specific entry in the bgg things DB. Things are the core
    abstraction for games, expansions, etc...
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc3
    """

    def __init__(self, *args: int) -> None:
        self.__ids: Sequence[int] = args
        self.__types: Sequence[str] = []

    def of_type(self, *args: str) -> "RequestThing":
        self.__types = args
        return self

    def query(
        self,
        with_versions: bool = False,
        with_videos: bool = False,
        with_stats: bool = False,
        with_historical: bool = False,
        with_marketplace: bool = False,
        with_comments: bool = False,
    ) -> ThingItems:
        flags = []
        if with_versions:
            flags.append("versions")
        if with_videos:
            flags.append("videos")
        if with_stats:
            flags.append("stats")
        if with_historical:
            flags.append("historical")
        if with_marketplace:
            flags.append("marketplace")
        if with_comments:
            flags.append("comments")
        return self._fetch(flags=flags)

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "thing"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {"id": ",".join([f"{id}" for id in self.__ids])}

        if self.__types:
            params.update({"type": ",".join(self.__types)})

        if kwargs["flags"]:
            params.update({"flag": "1" for flags in kwargs["flags"]})

        return params

    def _build_response(self, root: ET.Element) -> ThingItems:
        return ThingItems(root)

    def _should_cache_request(self) -> bool:
        return len(self.__ids) == 1

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        if len(self.__ids) > 1:
            # Disable cache for multiple-point queries
            return None

        return f"{firstx(self.__ids)}"
