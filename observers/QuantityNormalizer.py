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
    def __init__(self, logic: Logic, percentile: float = 0.99) -> None:
        self.__logic = logic
        self.__percentile = percentile

    def __str__(self) -> str:
        results = self.__logic.getResults()
        total = sum(results.values())
        accumulated = 0
        output = [f"Total: {total}"]
        for i in range(max(results.keys())):
            accumulated += results.get(i, 0)
            output.append(f"{i}: {accumulated}")
            if accumulated / total > self.__percentile:
                break
        return ",".join(output)
