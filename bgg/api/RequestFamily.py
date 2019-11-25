import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence

from ..model import Items, family
from ..utils import firstx
from .RequestBase import RequestBase


class RequestFamily(RequestBase[Items[family.Item]]):
    """
    Things could be grouped in abstract 'families' based on a commonality.
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc4
    """

    def __init__(self, *args: int) -> None:
        self.__ids: Sequence[int] = args
        self.__types: Sequence[str] = []

    def of_types(self, *args: str) -> "RequestFamily":
        self.__types = args
        return self

    def query(self) -> Items[family.Item]:
        return self._fetch()

    def query_first(self) -> family.Item:
        if len(self.__ids) > 1:
            raise Exception(f"Requested more than 1 item, use 'query' instead")

        items = self.query()

        if len(items) > 1:
            raise Exception(f"There is more than one item in the response {len(items)}")

        return firstx(items)

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "family"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {"id": ",".join([f"{id}" for id in self.__ids])}

        if self.__types:
            params.update({"type": ",".join(self.__types)})

        return params

    def _build_response(self, root: ET.Element, **kwargs) -> Items[family.Item]:
        return Items(root, lambda item_elem: family.Item(item_elem))

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        return None

        if len(self.__ids) > 1:
            # Disable cache for multiple-point queries
            return None

        if len(self.__types) > 0:
            # Disable cache for type filtering
            return None

        return f"{firstx(self.__ids)}"
