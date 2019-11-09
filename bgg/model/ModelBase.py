import abc
import xml.etree.ElementTree as ET
from typing import Optional

from ..utils import nonthrows


class ModelBase:
    @abc.abstractclassmethod
    def _rootTagName(cls) -> str:
        pass

    def __init__(self, root: ET.Element) -> None:
        if root.tag != self._rootTagName():
            raise Exception(
                f"Expected root tag '{self._rootTagName()}' but got '{root.tag}'"
            )

        self._root = root

    def _field(self, name: str) -> str:
        return nonthrows(
            self._root.get(name),
            f"Attribute '{name}' missing in '{self._rootTagName()}'",
        )

    def _child(self, tag_name: str) -> ET.Element:
        return nonthrows(
            self._root.find(tag_name),
            f"Child '{tag_name}' missing in '{self._rootTagName()}'",
        )

    def _child_value(self, tag_name: str) -> str:
        return nonthrows(
            self._child(tag_name).get("value"),
            f"Value attribute missing for '{tag_name}' in '{self._rootTagName()}'",
        )

    def _child_text(self, tag_name: str) -> str:
        return nonthrows(
            self._child(tag_name).text,
            f"'{tag_name}' has no inner text in '{self._rootTagName()}'",
        )

    @staticmethod
    def _stringToBool(str) -> bool:
        if str == "0":
            return False
        elif str == "1":
            return True
        else:
            raise Exception(f"Unexpected boolean value {str}")

    @staticmethod
    def _nonifyStr(x: str) -> Optional[str]:
        return None if x == "" else x

    @staticmethod
    def _nonifyInt(x: str) -> Optional[int]:
        return None if x == "" or x == "0" else int(x)
