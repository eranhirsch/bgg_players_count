import collections
import datetime
from typing import Dict, Iterable, Iterator, List, Sized, Tuple

from ..utils import firstx, nonthrows
from .ModelBase import ModelBase


class Name(ModelBase):
    def _rootTagName(self) -> str:
        return "name"

    def type(self) -> str:
        return self._field("type")

    def sort_index(self) -> int:
        return int(self._field("sortindex"))

    def value(self) -> str:
        return self._field("value")


class PollResult(ModelBase):
    def _rootTagName(self) -> str:
        return "result"

    def value(self) -> str:
        return self._field("value")

    def num_votes(self) -> int:
        return int(self._field("numvotes"))

    def level(self) -> int:
        """This field is optional and only shows up in the language_dependance poll"""
        return int(self._field("level"))


class PollResults(ModelBase, Sized, Iterable[PollResult]):
    def _rootTagName(self) -> str:
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
    def _rootTagName(self) -> str:
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
    def _rootTagName(self) -> str:
        return "link"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def value(self) -> str:
        return self._field("value")


class ThingItem(ModelBase):
    @classmethod
    def _rootTagName(cls) -> str:
        return "item"

    def type(self) -> str:
        return self._field("type")

    def id(self) -> int:
        return int(self._field("id"))

    def thumbnail(self) -> str:
        return nonthrows(nonthrows(self._root.find("thumbnail")).text)

    def image(self) -> str:
        return nonthrows(nonthrows(self._root.find("image")).text)

    def names(self) -> Iterator[Name]:
        """Raw data, prefer calling the primary_name method instead"""
        names = nonthrows(self._root.find("name"))
        for name in names:
            yield Name(name)

    def primary_name(self) -> str:
        return next(name for name in self.names() if name.type() == "primary").value()

    def description(self) -> str:
        return nonthrows(nonthrows(self._root.find("description")).text)

    def year_published(self) -> int:
        return int(self._child_value("yearpublished"))

    def player_count(self) -> Tuple[int, int]:
        """The official (published) player count limits for the game"""
        min = int(self._child_value("minplayers"))
        max = int(self._child_value("maxplayers"))
        return (min, max)

    def polls(self) -> Iterator[Poll]:
        """Raw data, prefer calling the specific poll methods"""
        for poll in nonthrows(self._root.find("poll")):
            yield Poll(poll)

    def suggested_num_players(self) -> Dict[str, Tuple[int, int, int]]:
        poll = next(
            poll for poll in self.polls() if poll.name() == "suggested_numplayers"
        )
        results = {results.num_players(): results.as_dict() for results in poll}
        return {
            num_players: (ranks["Best"], ranks["Recommended"], ranks["Not Recommended"])
            for num_players, ranks in results.items()
        }

    def suggested_player_age(self) -> Dict[str, int]:
        return (
            next(poll for poll in self.polls() if poll.name() == "suggested_playerage")
            .only_results()
            .as_dict()
        )

    def language_dependence(self) -> Dict[str, int]:
        return (
            next(poll for poll in self.polls() if poll.name() == "language_dependence")
            .only_results()
            .as_dict()
        )

    def playing_time(self) -> Tuple[datetime.timedelta, datetime.timedelta]:
        min = int(self._child_value("minplaytime"))
        max = int(self._child_value("maxplaytime"))
        return (datetime.timedelta(minutes=min), datetime.timedelta(minutes=max))

    def min_age(self) -> int:
        """Minimum playing age as defined by the publisher"""
        return int(self._child_value("minage"))

    def links_raw(self) -> Iterator[Link]:
        """Raw data, prefer calling links instead"""
        for link in nonthrows(self._root.find("link")):
            yield Link(link)

    def links(self) -> Dict[str, List[Tuple[int, str]]]:
        out: Dict[str, List[Tuple[int, str]]] = collections.defaultdict(list)
        for link in self.links_raw():
            out[link.type()].append((link.id(), link.value()))
        return out
