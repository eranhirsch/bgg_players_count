from typing import Dict

from bgg.model import play


class QuantityCountLogic:
    __quantities: Dict[int, int]

    def __init__(self) -> None:
        self.__quantities = {}

    def visit(self, play: play.Play) -> None:
        quantity = play.quantity()
        try:
            self.__quantities[quantity] += 1
        except KeyError:
            self.__quantities[quantity] = 1

    def getResults(self) -> Dict[int, int]:
        return self.__quantities


class QuantityCountCLIPresenter:
    def __init__(self, logic: QuantityCountLogic) -> None:
        self.__logic = logic

    def render(self) -> str:
        quantities = self.__logic.getResults()
        return "\n".join(
            ["Quantities\tCount"]
            + [
                f"{quantity}\t{count}"
                for count, quantity in sorted(
                    list(quantities.items()), key=lambda item: item[1], reverse=True
                )
            ]
        )
