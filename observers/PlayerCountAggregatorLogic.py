from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 10


class Results:
    __complete: Dict[int, int] = {}
    __incomplete: Dict[int, int] = {}

    def bump(self, bucket: int, quantity: int, complete: bool) -> None:
        try:
            if complete:
                self.__complete[bucket] += quantity
            else:
                self.__incomplete[bucket] += quantity
        except KeyError:
            if complete:
                self.__complete[bucket] = quantity
            else:
                self.__incomplete[bucket] = quantity

    def complete(self) -> Dict[int, int]:
        return self.__complete

    def incomplete(self) -> Dict[int, int]:
        return self.__incomplete


class PlayerCountAggregatorLogic:
    __results = Results()

    def visit(self, play: Play) -> None:
        players = play.players()
        self.__results.bump(
            len(players) if players else 0,
            min(play.quantity(), SANITY_MAX_QUANTITY),
            not play.is_incomplete(),
        )

    def getResults(self) -> Results:
        return self.__results
