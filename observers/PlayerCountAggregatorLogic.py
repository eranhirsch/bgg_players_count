import re
from enum import Enum, auto
from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 10

# A list of apps and platforms that allow digital play. KEEP LOWERCASE!
DIGITAL_LOCATIONS_RE = [
    re.compile(re_str, re.IGNORECASE)
    for re_str in [
        r"(\w+\.)?isotropic(\.org)?",
        r"(the )?internet",
        r"a smartphone",
        r"app",
        r"b(oard)? ?g(ame)? ?a(rena)?(\.com)?",
        r"boiteajeux(\.net)?",
        r"emulator",
        r"ios",
        r"ipad",
        r"iphone",
        r"on ?line",
        r"pc",
        r"steam",
        r"switch",
        r"tabletop simulator",
        r"web",
    ]
]


class ResultsCategory(Enum):
    COMPLETE = auto()
    INCOMPLETE = auto()
    DIGITAL = auto()


TCategoryResult = Dict[int, int]
TResults = Dict[ResultsCategory, TCategoryResult]


class PlayerCountAggregatorLogic:
    __results: TResults = {}

    def __init__(self) -> None:
        for cat in ResultsCategory:
            self.__results[cat] = {}

    def visit(self, play: Play) -> None:
        location = play.location()
        if location and any([re.match(location) for re in DIGITAL_LOCATIONS_RE]):
            category = ResultsCategory.DIGITAL
        elif play.is_incomplete():
            category = ResultsCategory.INCOMPLETE
        else:
            category = ResultsCategory.COMPLETE
        players = play.players()
        self.__bump(
            category,
            len(players) if players else 0,
            min(play.quantity(), SANITY_MAX_QUANTITY),
        )

    def getResults(self) -> TResults:
        return self.__results

    def __bump(self, category: ResultsCategory, bucket: int, quantity: int) -> None:
        try:
            self.__results[category][bucket] += quantity
        except KeyError:
            self.__results[category][bucket] = quantity
