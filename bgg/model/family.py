from typing import Iterable, Iterator, Optional, Sized, Tuple

from ..utils import nonthrows
from . import Link, Name
from .ModelBase import ModelBase


class Item(ModelBase, Iterable[Tuple[int, str]]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "item"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def thumbnail(self) -> Optional[str]:
        try:
            return self._child_text("thumbnail")
        except TypeError:
            return None

    def image(self) -> str:
        return self._child_text("image")

    def primary_name(self) -> str:
        return next(
            name for name in self.__names_raw() if name.type() == "primary"
        ).value()

    def description(self) -> str:
        return self._child_text("description")

    def __iter__(self) -> Iterator[Tuple[int, str]]:
        for link in self.__links_raw():
            if link.type() != "boardgamefamily":
                raise Exception(f"Unexpected link type '{link.type()}'")

            if not link.is_inbound():
                raise Exception(f"Unexpected non-inbound link")

            yield (link.id(), link.value())

    def __names_raw(self) -> Iterator[Name]:
        """Raw data, prefer calling the primary_name method instead"""
        for name in nonthrows(self._root.findall("name")):
            yield Name(name)

    def __links_raw(self) -> Iterator[Link]:
        """Raw data, prefer calling links instead"""
        for link in nonthrows(self._root.findall("link")):
            yield Link(link)


class Items(ModelBase, Sized, Iterable[Item]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "items"

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[Item]:
        for item in self._root:
            yield Item(item)
