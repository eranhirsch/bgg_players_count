from typing import Optional, TypeVar

T = TypeVar("T")


def nullthrows(something: Optional[T], msg: str = None) -> T:
    if something is None:
        raise TypeError(msg or "Unexpected Null")
    return something
