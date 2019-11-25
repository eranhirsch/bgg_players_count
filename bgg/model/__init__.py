from .ModelBase import ModelBase


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
