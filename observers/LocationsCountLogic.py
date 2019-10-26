from typing import Dict

from bgg.model.Play import Play

from .PlayerCountAggregatorLogic import DIGITAL_LOCATIONS_RE


class LocationsCountLogic:
    __locations: Dict[str, int] = {}

    def visit(self, play: Play):
        location = play.location()
        if not location:
            return

        if any([re.match(location) for re in DIGITAL_LOCATIONS_RE]):
            return

        location = location.lower()
        try:
            self.__locations[location] += 1
        except KeyError:
            self.__locations[location] = 1

    def getResults(self) -> Dict[str, int]:
        return self.__locations
