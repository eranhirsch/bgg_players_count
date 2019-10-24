from typing import Tuple

from ..utils import nonthrows
from .ModelBase import ModelBase


class SearchItem(ModelBase):
    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def name(self) -> Tuple[str, str]:
        name_elem = nonthrows(self._root.find("name"))
        return (nonthrows(name_elem.get("value")), nonthrows(name_elem.get("type")))

    def yearPublished(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("yearpublished")).get("value")))

    def _rootTagName(self) -> str:
        return "item"
