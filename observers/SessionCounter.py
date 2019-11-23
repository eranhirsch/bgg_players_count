from typing import List

from bgg.model import play


class Logic:
    def __init__(self) -> None:
        self.__results: int = 0

    def visit(self, play: play.Play) -> None:
        self.__results += 1

    def getResults(self) -> int:
        return self.__results


class Presenter:
    @staticmethod
    def column_names() -> List[str]:
        return ["Sessions"]

    def __init__(self, logic: Logic) -> None:
        self.__logic = logic

    def __str__(self) -> str:
        return f"{self.__logic.getResults()}"
