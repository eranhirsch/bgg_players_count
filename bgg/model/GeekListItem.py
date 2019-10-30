import datetime

from ..utils import nonthrows
from .ModelBase import ModelBase

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"


class GeekListItem(ModelBase):
    def id(self) -> int:
        return int(self._field("id"))

    def object_type(self) -> str:
        return self._field("objecttype")

    def sub_type(self) -> str:
        return self._field("subtype")

    def object_id(self) -> int:
        return int(self._field("objectid"))

    def object_name(self) -> str:
        return self._field("objectname")

    def user_name(self) -> str:
        return self._field("username")

    def post_date(self) -> datetime.date:
        return datetime.datetime.strptime(self._field("postdate"), DATE_FORMAT)

    def edit_date(self) -> datetime.date:
        return datetime.datetime.strptime(self._field("editdate"), DATE_FORMAT)

    def thumbs(self) -> int:
        return int(self._field("thumbs"))

    def image_id(self) -> int:
        return int(self._field("imageid"))

    def body(self) -> str:
        return nonthrows(nonthrows(self._root.find("body")).text)

    def _rootTagName(self) -> str:
        return "item"
