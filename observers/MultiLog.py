import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

from bgg.model import play


class Logic:
    def __init__(self) -> None:
        self.__results: Dict[Tuple[int, datetime.date], int] = defaultdict(int)

    def visit(self, play: play.Play) -> None:
        date = play.date()
        if not date:
            return
        self.__results[(play.user_id(), date)] += 1

    def getResults(self) -> Dict[Tuple[int, datetime.date], int]:
        return self.__results


class Presenter:
    @staticmethod
    def column_names() -> List[str]:
        return [
            "total",
            "duplicate_entries",
            "duplicate_total",
            "total_users",
            "users_with_duplicates",
        ]

    def __init__(self, logic: Logic, separator: str = "\t") -> None:
        self.__logic = logic
        self.__separator = separator

    def __str__(self) -> str:
        results = self.__logic.getResults()
        out = [
            len(results),
            sum([1 for count in results.values() if count > 1]),
            sum([count for count in results.values() if count > 1]),
            len({entry[0] for entry in results.keys()}),
            len({item[0][0] for item in results.items() if item[1] > 1}),
        ]
        return self.__separator.join([str(field) for field in out])
