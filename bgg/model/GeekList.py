import datetime
from typing import Iterable, Iterator, Sized, Tuple

from .GeekListItem import GeekListItem
from .ModelBase import ModelBase


class GeekList(ModelBase, Sized, Iterable):
    @classmethod
    def _rootTagName(cls) -> str:
        return "geeklist"

    def id(self) -> int:
        return int(self._field("id"))

    def post_date(self) -> datetime.date:
        # The API also returns a human-readable version in 'postdate'
        return datetime.date.fromtimestamp(int(self._child_text("postdate_timestamp")))

    def edit_date(self) -> datetime.date:
        return datetime.date.fromtimestamp(int(self._child_text("editdate_timestamp")))

    def thumbs(self) -> int:
        return int(self._child_text("thumbs"))

    def user_name(self) -> str:
        return self._child_text("username")

    def title(self) -> str:
        return self._child_text("title")

    def description(self) -> str:
        return self._child_text("description")

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
        return int(self._child_text("numitems"))
