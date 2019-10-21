from typing import Optional, TypeVar

T = TypeVar("T")


def nonthrows(something: Optional[T], msg: str = None) -> T:
    if something is None:
        raise TypeError(msg or "Unexpected Null")
    return something
