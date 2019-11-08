from typing import Iterable, Iterator, Sized

from .ModelBase import ModelBase
from .ThingItem import ThingItem


class ThingItems(ModelBase, Sized, Iterable[ThingItem]):
    def _rootTagName(self) -> str:
        return "items"

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[ThingItem]:
        for item in self._root:
            yield ThingItem(item)
