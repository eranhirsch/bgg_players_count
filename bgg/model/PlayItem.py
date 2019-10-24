from typing import List

from ..utils import nonthrows
from .ModelBase import ModelBase


class PlayItem(ModelBase):
    def rootTagName(self) -> str:
        return "item"

    def name(self) -> str:
        return self._field("name")

    def objectType(self) -> str:
        return self._field("objecttype")

    def objectID(self) -> int:
        return int(self._field("objectid"))

    def subTypes(self) -> List[str]:
        return [
            nonthrows(subtype.get("value"))
            for subtype in list(nonthrows(self._root.find("subtypes")))
        ]
