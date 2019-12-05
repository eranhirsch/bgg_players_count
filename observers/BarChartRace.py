import abc
import datetime
from collections import defaultdict
from typing import (
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from bgg.model import play


class Month:
    @staticmethod
    def fromDate(dt: datetime.date, aggr_by: int = 1) -> "Month":
        if 12 % aggr_by != 0:
            raise Exception(f"{aggr_by} is not a divisor of 12!")

        return Month(dt.year, (((dt.month - 1) // aggr_by) + 1) * aggr_by)

    def __init__(self, year: int, month: int) -> None:
        self.__year = year

        if month > 12 or month < 0:
            raise Exception(f"Bad month {month}")

        self.__month = month

    def __iadd__(self, months: int) -> "Month":
        new_year = self.__year + ((self.__month + months - 1) // 12)
        new_month = (self.__month + months) % 12
        if new_month == 0:
            # Fix modulo issue with December
            new_month = 12
        return Month(new_year, new_month)

    def __lt__(self, other: "Month") -> bool:
        if self.__year < other.__year:
            return True

        if self.__year == other.__year:
            return self.__month < other.__month

        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Month):
            return NotImplemented
        return self.__year == other.__year and self.__month == other.__month

    def __str__(self) -> str:
        return f"{self.__year}-{self.__month:02d}"

    def __hash__(self) -> int:
        return hash(str(self))


class DateRange(Iterable[Month]):
    def __init__(self, start: Month, end: Month, step: int = 1) -> None:
        self.__start = start
        self.__end = end
        self.__step = step

    def __iter__(self) -> Iterator[Month]:
        curr = self.__start
        while curr < self.__end:
            yield curr
            curr += self.__step


T = TypeVar("T")


class MonthlyLogic(Generic[T]):
    @abc.abstractclassmethod
    def _countable_item(cls, play: play.Play) -> T:
        pass

    def __init__(self, aggr_by: int = 1) -> None:
        self.__results: Dict[Month, Set[T]] = defaultdict(set)
        self._aggr_by = aggr_by

    def visit(self, play: play.Play) -> None:
        date = play.date()
        if not date:
            return

        month = Month.fromDate(date, self._aggr_by)
        self.__results[month].add(self._countable_item(play))

    def getResults(self) -> Dict[Month, Set[T]]:
        return self.__results


class UniquePlaysLogic(MonthlyLogic[Tuple[int, Optional[datetime.date]]]):
    @classmethod
    def _countable_item(cls, play: play.Play) -> Tuple[int, Optional[datetime.date]]:
        return (play.user_id(), play.date())


class UniqueUsersLogic(MonthlyLogic[int]):
    @classmethod
    def _countable_item(cls, play: play.Play) -> int:
        return play.user_id()


class Presenter:
    @staticmethod
    def column_names(range: DateRange) -> List[str]:
        return [f"{month}-30" for month in range]

    def __init__(
        self,
        logic: MonthlyLogic,
        range: DateRange,
        min_year: Optional[int],
        separator: str = "\t",
    ) -> None:
        self.__logic = logic
        self.__range = range
        self.__separator = separator
        self.__min_year = min_year

    def __str__(self) -> str:
        results = self.__logic.getResults()
        counts = [
            str(
                0
                if self.__min_year and month < Month(self.__min_year, 1)
                else len(results.get(month, {}))
            )
            for month in self.__range
        ]
        return self.__separator.join(counts)
