from typing import Iterable, Iterator, Sized

from .ModelBase import ModelBase
from .Play import Play


class Plays(ModelBase, Sized, Iterable[Play]):
    def rootTagName(self) -> str:
        return "plays"

    def total(self) -> int:
        return int(self._field("total"))

    def page(self) -> int:
        return int(self._field("page"))

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[Play]:
        for child in self._root:
            try:
                yield Play(child)
            except Exception:
                # print(f"Skipping element because of error: {e}")

                # TODO: Temporarily don't allow failed parsing so we can find
                # all the quirks of the API
                raise

    def __str__(self) -> str:
        return f"Plays/Total: {self.total()}, Page: {self.page()}, Plays Count: {len(self)}"
