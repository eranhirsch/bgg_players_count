import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence

from ..model import family
from .RequestBase import RequestItemsBase


class RequestFamily(RequestItemsBase[family.Item]):
    """
    Things could be grouped in abstract 'families' based on a commonality.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc4
    """

    def __init__(self, *args: int) -> None:
        super().__init__(*args)
        self.__types: Sequence[str] = []

    def of_types(self, *args: str) -> "RequestFamily":
        self.__types = args
        return self

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "family"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = super()._api_params(**kwargs)

        if self.__types:
            params.update({"type": ",".join(self.__types)})

        return params

    def _build_item(self, item_elem: ET.Element) -> family.Item:
        return family.Item(item_elem)

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        cache_file_name = super()._cache_file_name(**kwargs)

        if len(self.__types) > 0:
            # Disable cache for type filtering
            return None

        return cache_file_name
