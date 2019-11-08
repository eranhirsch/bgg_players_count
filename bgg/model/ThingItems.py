from .ModelBase import ModelBase


class ThingItems(ModelBase):
    def _rootTagName(self) -> str:
        return "items"
