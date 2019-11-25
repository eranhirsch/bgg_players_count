from typing import Callable, Generic, Iterable, Iterator, Sized, TypeVar
from xml.etree import ElementTree as ET

from .ModelBase import ModelBase

TModel = TypeVar("TModel", bound=ModelBase)


class Items(ModelBase, Generic[TModel], Sized, Iterable[TModel]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "items"

    def __init__(
        self, root: ET.Element, factory: Callable[[ET.Element], TModel]
    ) -> None:
        super().__init__(root)
        self.__factory = factory

    def total(self) -> int:
        return int(self._field("total"))

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[TModel]:
        for child in self._root:
            yield self.__factory(child)


class Name(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "name"

    def type(self) -> str:
        return self._field("type")

    def sort_index(self) -> int:
        return int(self._field("sortindex"))

    def value(self) -> str:
        return self._field("value")


class Link(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "link"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def value(self) -> str:
        return self._field("value")

    def is_inbound(self) -> bool:
        raw = self._root.get("inbound")
        return True if raw == "true" else False
