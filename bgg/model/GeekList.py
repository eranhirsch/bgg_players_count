import datetime
from typing import Iterable, Iterator, Sized, Tuple

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

    def filter(self, *args: Tuple[str, str]) -> Iterator[GeekListItem]:
        for item in self:
            if (item.object_type(), item.sub_type()) in args:
                yield item
            else:
                print(
                    f"Skipping ({item.object_id()}): {item.object_name()}/Wrong type: {item.object_type()}/{item.sub_type()}"
                )

    def __iter__(self) -> Iterator[GeekListItem]:
        for item in self._root.findall("item"):
            yield GeekListItem(item)

    def __len__(self) -> int:
        return int(nonthrows(nonthrows(self._root.find("numitems")).text))
