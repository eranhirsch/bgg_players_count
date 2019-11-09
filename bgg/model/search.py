from typing import Iterable, Iterator, Sized, Tuple

from ..utils import nonthrows
from .ModelBase import ModelBase


class Item(ModelBase):
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


class Items(ModelBase, Sized, Iterable[Item]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "items"

    def total(self) -> int:
        return int(self._field("total"))

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[Item]:
        for child in self._root:
            try:
                yield Item(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise
