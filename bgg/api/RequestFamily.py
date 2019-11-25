import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence

from ..model import family
from ..utils import firstx
from .RequestBase import RequestBase


class RequestFamily(RequestBase):
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

    def query(self) -> family.Items:
        return self._fetch()

    def _api_version(self) -> int:
        return 2

    def _api_path(self, **kwargs) -> str:
        return "family"

    def _api_params(self, **kwargs) -> Dict[str, str]:
        params = {"id": ",".join([f"{id}" for id in self.__ids])}

        if self.__types:
            params.update({"type": ",".join(self.__types)})

        return params

    def _build_response(self, root: ET.Element, **kwargs) -> family.Items:
        return family.Items(root)

    def _cache_file_name(self, **kwargs) -> Optional[str]:
        return None

        if len(self.__ids) > 1:
            # Disable cache for multiple-point queries
            return None

        if len(self.__types) > 0:
            # Disable cache for type filtering
            return None

        return f"{firstx(self.__ids)}"
