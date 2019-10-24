from typing import List

from ..utils import nonthrows
from .ModelBase import ModelBase


class PlayItem(ModelBase):
    def rootTagName(self) -> str:
        return "item"

    def name(self) -> str:
        return nonthrows(self._root.get("name"))

    def objectType(self) -> str:
        return nonthrows(self._root.get("objecttype"))

    def objectID(self) -> int:
        return int(nonthrows(self._root.get("objectid")))

    def subTypes(self) -> List[str]:
        return [
            nonthrows(subtype.get("value"))
            for subtype in list(nonthrows(self._root.find("subtypes")))
        ]

    def __str__(self) -> str:
        return f"PlayItem/Name: {self.name()}, Type: {self.objectType()}, ID: {self.objectID()}, Subtypes: {':'.join(self.subTypes())}"
