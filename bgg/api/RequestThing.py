import xml.etree.ElementTree as ET
from typing import Dict, Iterator, Optional, Sequence, Set

from ..model import thing
from ..utils import firstx
from .RequestBase import RequestBase

KNOWN_FLAGS = {
    "stats",
    "",
    "video",
    "historical",
    "marketplace",
    "comments",
    "rating_comments",
}


class RequestThing(RequestBase[thing.Items]):
    """
    A request for a specific entry in the bgg things DB. Things are the core
    abstraction for games, expansions, etc...
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc3
    """

    def __init__(self, *args: int) -> None:
        self.__ids: Sequence[int] = args
        self.__types: Sequence[str] = []
        self.__flags: Set[str] = set()

    def of_types(self, *args: str) -> "RequestThing":
        self.__types = args
        return self

    def with_flags(self, *flags_raw: str) -> "RequestThing":
        flags = set(flags_raw)

        if not flags.issubset(KNOWN_FLAGS):
            raise Exception(f"Unknown flags {', '.join(flags-KNOWN_FLAGS)}")

        if "video" in flags:
            raise NotImplementedError("Videos API currently not supported")
        if "historical" in flags:
            raise NotImplementedError("Historical API currently not supported")
        if "marketplace" in flags:
            raise NotImplementedError("Marketplace API currently not supported")
        if "comments" in flags:
            if "rating_comments" in flags:
                raise Exception(
                    "Can't use both comments and rating_comments for thing requests"
                )
            raise NotImplementedError("Comments API currently not supported")
        if "rating_comments" in flags:
            raise NotImplementedError("Rating Comments API currently not supported")

        self.__flags = set(*flags)
        return self

    def query(self) -> Iterator[thing.Item]:
        for item in self._fetch():
            yield item.with_flags(self.__flags)

    def query_first(self) -> thing.Item:
        if len(self.__ids) > 1:
            raise Exception(f"Requested more than 1 item, use 'query' instead")

        items_iter = iter(self.query())
        item = next(items_iter)

        try:
            next(items_iter)
            raise Exception(f"Response had more than 1 item in it!")
        except StopIteration:
            # If we caught a StopIteration it means the iterator had no more
            # values in it; Which is what we want
            return item

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "thing"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {"id": ",".join([f"{id}" for id in self.__ids])}

        if self.__types:
            params.update({"type": ",".join(self.__types)})

        if self.__flags:
            params.update({flag: "1" for flag in self.__flags})

        return params

    def _build_response(self, root: ET.Element, **kwargs) -> thing.Items:
        return thing.Items(root)

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        if len(self.__ids) > 1:
            # Disable cache for multiple-point queries
            return None

        if len(self.__types) > 0:
            # Disable cache for type filtering
            return None

        if len(self.__flags) > 1:
            # Flags might be mixed together and create too many different
            # combinations which basically return the same thing, so just
            # disabling caching for flags atm
            return None
        elif len(self.__flags) == 1:
            return f"{firstx(self.__ids)}_{firstx(self.__flags)}"
        else:
            return f"{firstx(self.__ids)}"
