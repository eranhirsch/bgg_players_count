from typing import Dict

from bgg.model import play

from .PlayerCountAggregator import DIGITAL_LOCATIONS_RE

NUM_LOCATIONS_TO_PRINT = 100


class Logic:
    __locations: Dict[str, Dict[str, int]]

    def __init__(self) -> None:
        self.__locations = {}
        self.__locations[Logic.__getLabel(True)] = {}
        self.__locations[Logic.__getLabel(False)] = {}

    def visit(self, play: play.Play) -> None:
        location = play.location()
        if not location:
            return

        location = location.strip()
        is_digital = any([re.match(location) for re in DIGITAL_LOCATIONS_RE])
        label = Logic.__getLabel(is_digital)

        location = location.lower()
        try:
            self.__locations[label][location] += 1
        except KeyError:
            self.__locations[label][location] = 1

    def getResults(self, is_digital: bool) -> Dict[str, int]:
        return self.__locations[Logic.__getLabel(is_digital)]

    @staticmethod
    def __getLabel(is_digital: bool) -> str:
        return "digital" if is_digital else "regular"


class CLIPresenter:
    def __init__(self, logic: Logic, is_digital: bool) -> None:
        self.__logic = logic
        self.__is_digital = is_digital

    def __str__(self) -> str:
        locations = self.__logic.getResults(self.__is_digital)
        return "\n".join(
            ["Location\tCount"]
            + [
                f"{location}\t{count}"
                for count, location in sorted(
                    list(locations.items()), key=lambda item: item[1], reverse=True
                )[:NUM_LOCATIONS_TO_PRINT]
            ]
        )
