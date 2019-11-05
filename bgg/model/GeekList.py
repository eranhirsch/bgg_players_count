import datetime
from typing import Iterable, Iterator, Sized

from ..utils import nonthrows
from .GeekListItem import GeekListItem
from .ModelBase import ModelBase


class GeekList(ModelBase, Sized, Iterable):
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

    def _rootTagName(self) -> str:
        return "geeklist"

    def __iter__(self) -> Iterator[GeekListItem]:
        items = self._root.findall("item")
        if not items:
            raise StopIteration("No item in list")

        for item in items:
            yield GeekListItem(item)

    def __len__(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("numitems")).text))
