from typing import Callable, Iterable, Optional, Sequence, TypeVar

T = TypeVar("T")
Traw = TypeVar("Traw")
Tout = TypeVar("Tout")


def nonthrows(something: Optional[T], msg: str = None) -> T:
    if something is None:
        raise TypeError(msg or "Unexpected Null")
    return something


def firstx(collection: Iterable[T]) -> T:
    return nonthrows(next(iter(collection)))


class LazySequence(Sequence[Tout]):
    def __init__(
        self, raw_collection: Sequence[Traw], fn: Callable[[Traw], Tout]
    ) -> None:
        self.__rawCollection = raw_collection
        self.__fn = fn

    # DO NOT TYPE THIS METHOD, mypy completely freaks out here
    def __getitem__(self, s_idx):
        if isinstance(s_idx, int):
            return self.__fn(self.__rawCollection.__getitem__(s_idx))
        return [self.__fn(raw) for raw in self.__rawCollection.__getitem__(s_idx)]

    def __len__(self) -> int:
        return len(self.__rawCollection)
