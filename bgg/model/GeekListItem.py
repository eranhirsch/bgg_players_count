from .ModelBase import ModelBase


class GeekListItem(ModelBase):
    def _rootTagName(self) -> str:
        return "item"
