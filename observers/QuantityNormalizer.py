from typing import Dict

from bgg.model import play


class Logic:
    def __init__(self) -> None:
        self.__results: Dict[int, int] = {}

    def visit(self, play: play.Play) -> None:
        quantity = play.quantity()
        try:
            self.__results[quantity] += 1
        except KeyError:
            self.__results[quantity] = 1

    def getResults(self) -> Dict[int, int]:
        return self.__results


class Presenter:
    def __init__(self, logic: Logic) -> None:
        self.__logic = logic

    def render(self, percentile: float = 0.9) -> str:
        results = self.__logic.getResults()
        total = sum(results.values())
        accumulated = 0
        for i in range(max(results.keys())):
            accumulated += results.get(i, 0)
            if accumulated / total > percentile:
                return f"{i}"
        raise Exception("Something went wrong")
