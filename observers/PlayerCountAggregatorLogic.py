from typing import Dict

from bgg.model.Play import Play

# Some people log really odd quantities for plays, like 50 and 100. These aren't
# very valuable to us so we cap it at a reasonable number and return that
SANITY_MAX_QUANTITY: int = 10


class PlayerCountAggregatorLogic:
    __playerCountAggr: Dict[int, int] = {}

    def visit(self, play: Play) -> None:
        if play.is_incomplete():
            return

        players = play.players() or []
        player_count = len(players)
        quantity = min(play.quantity(), SANITY_MAX_QUANTITY)
        try:
            self.__playerCountAggr[player_count] += quantity
        except KeyError:
            self.__playerCountAggr[player_count] = quantity

    def getResults(self) -> Dict[int, int]:
        return self.__playerCountAggr
