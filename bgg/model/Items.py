from typing import Iterable, Iterator, Sized

from .ModelBase import ModelBase
from .SearchItem import SearchItem


class Items(ModelBase, Sized, Iterable[SearchItem]):
    def rootTagName(self) -> str:
        return "items"

    def total(self) -> int:
        return int(self._fieldRaw("total"))

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[SearchItem]:
        for child in self._root:
            try:
                yield SearchItem(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise
