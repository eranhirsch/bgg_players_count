import datetime
from typing import Optional, Sequence, Sized

from ..utils import LazySequence, nonthrows
from .GeekListItem import GeekListItem
from .ModelBase import ModelBase


class GeekList(ModelBase, Sized):
    def id(self) -> int:
        return int(self._field("id"))

    def post_date(self) -> datetime.date:
        # The API also returns a human-readable version in 'postdate'
        return datetime.date.fromtimestamp(
            int(nonthrows(nonthrows(self._root.find("postdate_timestamp")).text))
        )

    def edit_date(self) -> datetime.date:
        return datetime.date.fromtimestamp(
            int(nonthrows(nonthrows(self._root.find("editdate_timestamp")).text))
        )

    def thumbs(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("thumbs")).text))

    def user_name(self) -> str:
        return nonthrows(nonthrows(self._root.find("username")).text)

    def title(self) -> str:
        return nonthrows(nonthrows(self._root.find("title")).text)

    def description(self) -> str:
        return nonthrows(nonthrows(self._root.find("description")).text)

    def items(self) -> Optional[Sequence[GeekListItem]]:
        items = self._root.findall("item")
        if not items:
            return None
        return LazySequence(items, lambda item: GeekListItem(item))

    def __len__(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("numitems")).text))

    def _rootTagName(self) -> str:
        return "geeklist"
