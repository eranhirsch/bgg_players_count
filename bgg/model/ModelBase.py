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
            raise Exception(f"Unexpected root tag: {root.tag}")

        self._root = root

    def _field(self, name) -> str:
        return nonthrows(self._root.get(name))

    def _child_value(self, tag_name: str) -> str:
        return nonthrows(nonthrows(self._root.find(tag_name)).get("value"))

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
