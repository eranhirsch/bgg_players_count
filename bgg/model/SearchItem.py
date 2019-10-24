from typing import Tuple

from ..utils import nonthrows
from .ModelBase import ModelBase


class SearchItem(ModelBase):
    def rootTagName(self) -> str:
        return "item"

    def type(self) -> str:
        return nonthrows(self._root.get("type"))

    def id(self) -> int:
        return int(nonthrows(self._root.get("id")))

    def name(self) -> Tuple[str, str]:
        name_elem = nonthrows(self._root.find("name"))
        return (nonthrows(name_elem.get("value")), nonthrows(name_elem.get("type")))

    def yearPublished(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("yearpublished")).get("value")))
