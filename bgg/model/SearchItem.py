from typing import Tuple

from ..utils import nonthrows
from .ModelBase import ModelBase


class SearchItem(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "item"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def name(self) -> Tuple[str, str]:
        name_elem = self._child("name")
        return (nonthrows(name_elem.get("value")), nonthrows(name_elem.get("type")))

    def yearPublished(self) -> int:
        return int(self._child_value("yearpublished"))
