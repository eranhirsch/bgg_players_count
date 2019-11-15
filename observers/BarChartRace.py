import datetime
from typing import Dict, Iterable, Iterator, List

from bgg.model import play


class Month:
    @staticmethod
    def fromDate(dt: datetime.date) -> "Month":
        return Month(dt.year, dt.month)

    def __init__(self, year: int, month: int) -> None:
        self.__year = year
        self.__month = month

    def year(self) -> int:
        return self.__year

    def month(self) -> int:
        return self.__month

    def __iadd__(self, months: int) -> "Month":
        return Month(
            self.__year + ((self.__month + months) // 12), (self.__month + months) % 12
        )

    def __lt__(self, other: "Month") -> bool:
        if self.__year < other.__year:
            return True

        if self.__year == other.__year:
            return self.__month < other.__month

        return False

    def __str__(self) -> str:
        return f"{self.__year}-{self.__month:02d}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Month):
            return NotImplemented
        return self.__year == other.__year and self.__month == other.__month

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)


class DateRange(Iterable[Month]):
    def __init__(self, start: Month, end: Month):
        self.__start = start
        self.__end = end

    def __iter__(self) -> Iterator[Month]:
        curr = self.__start
        while curr < self.__end:
            yield curr
            curr += 1


class Logic:
    def __init__(self) -> None:
        self.__results: Dict[Month, int] = {}

    def visit(self, play: play.Play) -> None:
        date = play.date()
        if not date:
            return

        month = Month.fromDate(date)
        try:
            self.__results[month] += 1
        except KeyError:
            self.__results[month] = 1

    def getResults(self) -> Dict[Month, int]:
        return self.__results


class Presenter:
    @staticmethod
    def column_names(range: DateRange) -> List[str]:
        return [str(month) for month in range]

    def __init__(self, logic: Logic, range: DateRange, separator: str = "\t") -> None:
        self.__logic = logic
        self.__range = range
        self.__separator = separator

    def render(self) -> str:
        results = self.__logic.getResults()
        return self.__separator.join(
            [f"{results.get(month, 0)}" for month in self.__range]
        )