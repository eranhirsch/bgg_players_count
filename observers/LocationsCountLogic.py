from typing import Dict

from bgg.model.Play import Play

from .PlayerCountAggregatorLogic import DIGITAL_LOCATIONS_RE

NUM_LOCATIONS_TO_PRINT = 100


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


class LocationsCountCLIPresenter:
    def __init__(self, logic: LocationsCountLogic) -> None:
        self.__logic = logic

    def render(self, **kwargs) -> str:
        locations = self.__logic.getResults(**kwargs)
        return "\n".join(
            ["Location\tCount"]
            + [
                f"{location}\t{count}"
                for count, location in sorted(
                    list(locations.items()), key=lambda item: item[1], reverse=True
                )[:NUM_LOCATIONS_TO_PRINT]
            ]
        )
