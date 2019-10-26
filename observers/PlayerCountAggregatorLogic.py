from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 10


class Results:
    playerCountAggr: Dict[int, int] = {}
    incomplete: int = 0


class PlayerCountAggregatorLogic:
    __results = Results()

    def visit(self, play: Play) -> None:
        if play.is_incomplete():
            self.__results.incomplete += 1
            return

        players = play.players() or []
        player_count = len(players)
        quantity = min(play.quantity(), SANITY_MAX_QUANTITY)
        try:
            self.__results.playerCountAggr[player_count] += quantity
        except KeyError:
            self.__results.playerCountAggr[player_count] = quantity

    def getResults(self) -> Results:
        return self.__results
