import re
from enum import Enum, auto
from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 20

# A list of apps and platforms that allow digital play.
DIGITAL_LOCATIONS_RE = [
    re.compile(re_str, re.IGNORECASE)
    for re_str in [
        # Devices:
        r"^(a )?smartphone$",
        r"^android$",
        r"^appstore$",
        r"^ios( device)?$",
        r"^ipad( air)?$",
        r"^iphone$",
        r"^pc$",
        r"^switch$",
        r"^tablet$",
        # Generic terms:
        r"^.*?\bapp\b.*?$",
        r"^(the )?internet$",
        r"^digitaa?l$",
        r"^electronic$",
        r"^emulator$",
        r"^mobile$",
        r"^on ?line( play)?$",
        r"^virtual$",
        r"^web$",
        # General-purpose services that offer digital versions of games:
        r"^(https?://)?(\w+\.)?isotropic(\.org/?)?$",
        r"^(https?://)?(m|www\.)?b(rett)? ?s(piel)? ?w(elt)?(\.de(/.*)?)?$",
        r"^(https?://)?(www\.)?b(oard)? ?g(ame)? ?a(rena)?(\.com/?| online)?$",
        r"^(https?://)?(www\.)?b(oard)? ?g(aming)?( |-)?o(nline)?(\.com/?)?$",
        r"^(https?://)?(www\.)?bo(i|î)te ?(a|à) ?jeux(\.net/?)?/?$",
        r"^(https?://)?(www\.)?d(ays)? ?of? ?w(onder)?(\.com/?)?$",
        r"^(https?://)?(www\.)?yucata(\.de)?/?$",
        r"^octgn$",
        r"^steam$",
        r"^t(able)?t(op)?( ?s(imulator)?)?$",
        r"^tabletopia(\.com)?$",
        # Game-specific services that offer a digital version:
        r"^(https?://)?(brass\.)?o(rder)? ?of? ?t(he)? ?h(ammer)?(\.com/?)?$",  # brass
        r"^(https?://)?(www\.)?j(inteki(\.net)?|\.?net)/?$",  # netrunner
    ]
]


class ResultsCategory(Enum):
    REGULAR = auto()
    INCOMPLETE = auto()
    DIGITAL = auto()


TCategoryResult = Dict[int, int]


class PlayerCountAggregatorLogic:
    __results: Dict[ResultsCategory, TCategoryResult] = {}

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

    def getResults(self) -> Dict[ResultsCategory, TCategoryResult]:
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


class PlayerCountAggregatorCLIPresenter:
    def __init__(self, logic: PlayerCountAggregatorLogic) -> None:
        self.__logic = logic

    def render(self) -> str:
        results = self.__logic.getResults()
        return "\n\n\n".join(
            [
                f"// {label.name} {'/'*(36-len(label.name))}\n{PlayerCountAggregatorCLIPresenter.__formatCounts(counts)}"
                for label, counts in results.items()
            ]
        )

    @staticmethod
    def __formatCounts(player_count_aggr: Dict[int, int]) -> str:
        if not player_count_aggr:
            return "NO DATA!"

        missing = player_count_aggr[0] if 0 in player_count_aggr else 0
        max_count = max(player_count_aggr.keys())
        total_plays = sum(player_count_aggr.values())
        out = ["Players\t\tPlays\tRatio\tRatio (No Unknowns)"]
        for players in range(max_count + 1):
            plays = player_count_aggr.get(players, 0)
            if players == 0:
                label = "Unknown\t"
            elif players == 1:
                label = "Solo\t"
            else:
                label = f"{players} Players"
            ratio = plays / total_plays
            ratio_no_unknowns = plays / (total_plays - missing) if players > 0 else 0
            out.append(
                f"{label}\t{plays}\t{100*ratio:2.0f}%\t{100*ratio_no_unknowns:2.0f}%"
            )

            if players == 0:
                # Just to make it look better
                out.append("-" * 40)

        out.append("=" * 40)
        out.append(f"Total:\t\t{total_plays}")
        return "\n".join(out)


class PlayerCountAggregatorCSVPresenter:
    def __init__(
        self, logic: PlayerCountAggregatorLogic, separator: str = "\t"
    ) -> None:
        self.__logic = logic
        self.__separator = separator

    def render(self) -> str:
        results = self.__logic.getResults()
        regular = results[ResultsCategory.REGULAR]
        digital = results[ResultsCategory.DIGITAL]
        incomplete = results[ResultsCategory.INCOMPLETE]

        total_regular = sum(regular.values())
        missing = regular[0] if 0 in regular else 0
        meaningful_entries = total_regular - missing
        players_ratios = [
            regular.get(player_count, 0) / meaningful_entries
            for player_count in range(1, max(regular.keys()) + 1)
        ]
        total_digital = sum(digital.values())
        total_incomplete = sum(incomplete.values())

        return self.__separator.join(
            map(
                lambda num: f"{num:.2f}",
                [
                    total_regular,
                    # Percent digital
                    total_digital / (total_digital + total_regular),
                    # Incomplete games (per mil)
                    100 * total_incomplete / (total_incomplete + total_regular),
                    # Data quality metric, percent of non-meaningful
                    missing / total_regular,
                    meaningful_entries,
                ]
                + players_ratios,
            )
        )
