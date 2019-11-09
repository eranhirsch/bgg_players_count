import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence, Set

from ..model import thing
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

    def of_types(self, *args: str) -> "RequestThing":
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
    ) -> thing.Items:
        flags: Set[str] = set()
        if with_versions:
            flags.add("versions")
        if with_videos:
            raise NotImplementedError("Videos API currently not supported")
        if with_stats:
            flags.add("stats")
        if with_historical:
            flags.add("historical")
        if with_marketplace:
            flags.add("marketplace")
        if with_comments:
            flags.add("comments")
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
            params.update({flag: "1" for flag in kwargs["flags"]})

        return params

    def _build_response(self, root: ET.Element, **kwargs) -> thing.Items:
        return thing.Items(root).with_flags(kwargs["flags"])

    def _should_cache_request(self) -> bool:
        return len(self.__ids) == 1

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        if len(self.__ids) > 1:
            # Disable cache for multiple-point queries
            return None

        if len(self.__types) > 0:
            # Disable cache for type filtering
            return None

        if len(kwargs["flags"]) > 0:
            # Flags might be mixed together and create too many different
            # combinations which basically return the same thing, so just
            # disabling caching for flags atm
            return None

        return f"{firstx(self.__ids)}"
