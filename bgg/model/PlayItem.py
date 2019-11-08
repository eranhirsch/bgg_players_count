from typing import List

from ..utils import nonthrows
from .ModelBase import ModelBase


class PlayItem(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "plays"

    def name(self) -> str:
        return self._field("name")

    def objectType(self) -> str:
        return self._field("objecttype")

    def objectID(self) -> int:
        return int(self._field("objectid"))

    def subTypes(self) -> List[str]:
        return [nonthrows(subtype.get("value")) for subtype in self._child("subtypes")]
