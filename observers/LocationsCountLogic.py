from typing import Dict

from bgg.model.Play import Play

from .PlayerCountAggregatorLogic import DIGITAL_LOCATIONS_RE


class LocationsCountLogic:
    __locations: Dict[str, Dict[str, int]]

    def __init__(self) -> None:
        self.__locations = {}
        self.__locations[LocationsCountLogic.__getLabel(True)] = {}
        self.__locations[LocationsCountLogic.__getLabel(False)] = {}

    def visit(self, play: Play) -> None:
        location = play.location()
        if not location:
            return

        location = location.strip()
        is_digital = any([re.match(location) for re in DIGITAL_LOCATIONS_RE])
        label = LocationsCountLogic.__getLabel(is_digital)

        location = location.lower()
        try:
            self.__locations[label][location] += 1
        except KeyError:
            self.__locations[label][location] = 1

    def getResults(self, is_digital: bool) -> Dict[str, int]:
        return self.__locations[LocationsCountLogic.__getLabel(is_digital)]

    @staticmethod
    def __getLabel(is_digital: bool) -> str:
        return "digital" if is_digital else "regular"
