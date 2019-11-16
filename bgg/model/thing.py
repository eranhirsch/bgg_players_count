import collections
import datetime
from typing import Dict, Iterable, Iterator, List, Optional, Set, Sized, Tuple

from ..utils import firstx, nonthrows
from .ModelBase import ModelBase


class Name(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "name"

    def type(self) -> str:
        return self._field("type")

    def sort_index(self) -> int:
        return int(self._field("sortindex"))

    def value(self) -> str:
        return self._field("value")


class PollResult(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "result"

    def value(self) -> str:
        return self._field("value")

    def num_votes(self) -> int:
        return int(self._field("numvotes"))

    def level(self) -> int:
        """This field is optional and only shows up in the language_dependance poll"""
        return int(self._field("level"))


class PollResults(ModelBase, Sized, Iterable[PollResult]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "results"

    def num_players(self) -> str:
        """This field is optional and only shows up in the player count poll"""
        return self._field("numplayers")

    def as_dict(self) -> Dict[str, int]:
        return {result.value(): result.num_votes() for result in self}

    def __iter__(self) -> Iterator[PollResult]:
        for result in self._root:
            yield PollResult(result)

    def __len__(self) -> int:
        return len(self._root)


class Poll(ModelBase, Sized, Iterable[PollResults]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "poll"

    def name(self) -> str:
        return self._field("name")

    def title(self) -> str:
        return self._field("title")

    def total_votes(self) -> int:
        return int(self._field("totalvotes"))

    def only_results(self) -> PollResults:
        """In most cases we only have one result, so we can skip the need to iterate over them and return the results directly instead"""

        if len(self) > 1:
            raise Exception(f"More than one results object found {len(self)}")

        return firstx(self)

    def __iter__(self) -> Iterator[PollResults]:
        for results in self._root:
            yield PollResults(results)

    def __len__(self) -> int:
        return len(self._root)


class Link(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "link"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def value(self) -> str:
        return self._field("value")


class Rank(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "rank"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def name(self, friendly: bool = False) -> str:
        return self._field("friendlyname" if friendly else "name")

    def value(self) -> Optional[int]:
        value = self._field("value")
        return int(value) if value != "Not Ranked" else None

    def bayesaverage(self) -> float:
        return float(self._field("bayesaverage"))


class Ratings(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "ratings"

    def users_rated(self) -> int:
        return int(self._child_value("usersrated"))

    def stats(self) -> Tuple[float, float, float, float]:
        return (
            float(self._child_value("average")),
            float(self._child_value("bayesaverage")),
            float(self._child_value("stddev")),
            float(self._child_value("median")),
        )

    def ranks(self) -> Dict[str, Rank]:
        return {rank.name(): rank for rank in self.__ranks_raw()}

    def market(self) -> Tuple[int, int, int, int]:
        return (
            int(self._child_value("owned")),
            int(self._child_value("trading")),
            int(self._child_value("wanting")),
            int(self._child_value("wishing")),
        )

    def num_comments(self) -> int:
        return int(self._child_value("numcomments"))

    def num_weights(self) -> int:
        return int(self._child_value("numweights"))

    def average_weight(self) -> float:
        return float(self._child_value("averageweight"))

    def __ranks_raw(self) -> Iterator[Rank]:
        for rank in self._child("ranks"):
            yield Rank(rank)


class Item(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "item"

    def with_flags(self, flags: Set[str]) -> "Item":
        self.__flags = flags
        return self

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def thumbnail(self) -> str:
        return self._child_text("thumbnail")

    def image(self) -> str:
        return self._child_text("image")

    def primary_name(self) -> str:
        return next(
            name for name in self.__names_raw() if name.type() == "primary"
        ).value()

    def description(self) -> str:
        self.__assert_type("boardgame")
        return self._child_text("description")

    def year_published(self) -> int:
        return int(self._child_value("yearpublished"))

    def player_count(self) -> Tuple[int, int]:
        """The official (published) player count limits for the game"""
        self.__assert_type("boardgame")
        min = int(self._child_value("minplayers"))
        max = int(self._child_value("maxplayers"))
        return (min, max)

    def suggested_num_players(self) -> Dict[str, Tuple[int, int, int]]:
        self.__assert_type("boardgame")
        poll = next(
            poll for poll in self.__polls_raw() if poll.name() == "suggested_numplayers"
        )
        results = {results.num_players(): results.as_dict() for results in poll}
        return {
            num_players: (ranks["Best"], ranks["Recommended"], ranks["Not Recommended"])
            for num_players, ranks in results.items()
        }

    def suggested_player_age(self) -> Dict[str, int]:
        self.__assert_type("boardgame")
        return (
            next(
                poll
                for poll in self.__polls_raw()
                if poll.name() == "suggested_playerage"
            )
            .only_results()
            .as_dict()
        )

    def language_dependence(self) -> Dict[str, int]:
        self.__assert_type("boardgame")
        return (
            next(
                poll
                for poll in self.__polls_raw()
                if poll.name() == "language_dependence"
            )
            .only_results()
            .as_dict()
        )

    def playing_time(self) -> Tuple[datetime.timedelta, datetime.timedelta]:
        self.__assert_type("boardgame")
        min = int(self._child_value("minplaytime"))
        max = int(self._child_value("maxplaytime"))
        return (datetime.timedelta(minutes=min), datetime.timedelta(minutes=max))

    def min_age(self) -> int:
        """Minimum playing age as defined by the publisher"""
        self.__assert_type("boardgame")
        return int(self._child_value("minage"))

    def links(self) -> Dict[str, List[Tuple[int, str]]]:
        out: Dict[str, List[Tuple[int, str]]] = collections.defaultdict(list)
        for link in self.__links_raw():
            out[link.type()].append((link.id(), link.value()))
        return out

    def product_code(self) -> str:
        self.__assert_type("boardgameversion")
        return self._child_value("productcode")

    def physical_dimensions(self) -> Tuple[float, float, float, float]:
        self.__assert_type("boardgameversion")
        return (
            float(self._child_value("width")),
            float(self._child_value("length")),
            float(self._child_value("depth")),
            float(self._child_value("weight")),
        )

    def versions(self) -> Iterator["Item"]:
        self.__assert_flag("versions")
        versions = self._child("versions")
        for version_raw in versions:
            version = Item(version_raw)
            if version.type() != "boardgameversion":
                raise Exception(
                    f"Found unexpected type {version.type()} in versions list"
                )
            yield version

    def ratings(self) -> Ratings:
        self.__assert_flag("stats")
        # Statistics themselves don't contain anything interesting so we skip
        # right into the ratings object inside it
        return Ratings(nonthrows(self._child("statistics").find("ratings")))

    def overall_rank(self) -> Optional[int]:
        self.__assert_type("boardgame")
        return self.ratings().ranks()[self.type()].value()

    def categories(self) -> List[str]:
        self.__assert_type("boardgame")
        return [
            rank.name(friendly=True).split(' ')[0]
            for rank in sorted(
                [
                    rank
                    for rank in self.ratings().ranks().values()
                    if rank.type() == "family"
                ],
                key=lambda rank: rank.value(),
            )
        ]

    def primary_category(self) -> Optional[str]:
        categories = self.categories()
        return categories[0] if categories else None

    def __assert_flag(self, flag: str) -> None:
        if flag not in self.__flags:
            raise Exception(
                f"{flag} data not requested! Add 'with_{flag}' to the query"
            )

    def __assert_type(self, type: str) -> None:
        if type != self.type():
            raise Exception(
                f"This data is only available for {type}, not for {self.type()}"
            )

    def __names_raw(self) -> Iterator[Name]:
        """Raw data, prefer calling the primary_name method instead"""
        for name in nonthrows(self._root.findall("name")):
            yield Name(name)

    def __polls_raw(self) -> Iterator[Poll]:
        """Raw data, prefer calling the specific poll methods"""
        for poll in nonthrows(self._root.findall("poll")):
            yield Poll(poll)

    def __links_raw(self) -> Iterator[Link]:
        """Raw data, prefer calling links instead"""
        for link in nonthrows(self._root.findall("link")):
            yield Link(link)


class Items(ModelBase, Sized, Iterable[Item]):
    @classmethod
    def _rootTagName(cls) -> str:
        return "items"

    def with_flags(self, flags: Set[str]) -> "Items":
        self.__flags = flags
        return self

    def only_item(self) -> Item:
        if len(self) > 1:
            raise Exception(f"There is more than one item in the response {len(self)}")
        return firstx(self)

    def __len__(self) -> int:
        return len(self._root)

    def __iter__(self) -> Iterator[Item]:
        for item in self._root:
            yield Item(item).with_flags(self.__flags)
