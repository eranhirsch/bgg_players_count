from typing import Iterable, Iterator, Set, Sized

from ..utils import firstx
from .ModelBase import ModelBase
from .ThingItem import ThingItem


class ThingItems(ModelBase, Sized, Iterable[ThingItem]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "items"

    def with_flags(self, flags: Set[str]) -> "ThingItems":
        self.__flags = flags
        return self

    def only_item(self) -> ThingItem:
        if len(self) > 1:
            raise Exception(f"There is more than one item in the response {len(self)}")
        return firstx(self)

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[ThingItem]:
        for item in self._root:
            yield ThingItem(item).with_flags(self.__flags)
