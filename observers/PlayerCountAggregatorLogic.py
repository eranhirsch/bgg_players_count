import re
from enum import Enum, auto
from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 10

# A list of apps and platforms that allow digital play.
DIGITAL_LOCATIONS_RE = [
    re.compile(re_str, re.IGNORECASE)
    for re_str in [
        r"^.*?\bapp\b.*?$",
        r"^(\w+\.)?isotropic(\.org)?$",
        r"^(a )?smartphone$",
        r"^(http://)?(www\.)?bo(i|î)te ?(a|à) ?jeux(\.net)?/?$",
        r"^(http://)?(www\.)?yucata(\.de)?/?$",
        r"^(the )?internet$",
        r"^android$",
        r"^appstore$",
        r"^b(oard)? ?g(ame)? ?a(rena)?(\.com)?$",
        r"^b(oard)? ?g(aming)?( |-)?o(nline)?(\.com)?$",
        r"^d(ays)? ?of? ?w(onder)?(\.com)?$",
        r"^digital$",
        r"^emulator$",
        r"^ios$",
        r"^ipad( air)?$",
        r"^iphone$",
        r"^on ?line$",
        r"^pc$",
        r"^steam$",
        r"^switch$",
        r"^t(able)?t(op)? ?s(imulator)?$",
        r"^tabletopia(\.com)?$",
        r"^web$",
    ]
]


class ResultsCategory(Enum):
    REGULAR = auto()
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
        players = play.players()
        self.__bump(
            PlayerCountAggregatorLogic.__categorize(play),
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

    @staticmethod
    def __categorize(play: Play) -> ResultsCategory:
        if play.is_incomplete():
            return ResultsCategory.INCOMPLETE

        location = play.location()
        if location and any(
            [digital.match(location.strip()) for digital in DIGITAL_LOCATIONS_RE]
        ):
            return ResultsCategory.DIGITAL

        return ResultsCategory.REGULAR
