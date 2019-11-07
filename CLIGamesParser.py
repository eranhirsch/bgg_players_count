from typing import Iterable, Iterator, List

from bgg.api.RequestList import RequestList
from bgg.api.RequestPlays import RequestPlays
from bgg.api.RequestSearch import RequestSearch
from bgg.utils import firstx

LIST_PREFIX = "list-"
FLAG_ALL_CACHED = "--all-cached"


class CLIGamesParser(Iterable[int]):
    def __init__(self, user_inputs: List[str]) -> None:
        self.__user_inputs = user_inputs

    def __iter__(self) -> Iterator[int]:
        for user_input in self.__user_inputs:
            if user_input == FLAG_ALL_CACHED:
                for id in RequestPlays.cached_queries():
                    yield int(id)

            if user_input.startswith(LIST_PREFIX):
                listid = int(user_input.split(LIST_PREFIX)[1])
                geeklist = RequestList(listid).fetch()
                print(
                    f'Iterating over geeklist "{geeklist.title()}" by {geeklist.user_name()} [last updated: {geeklist.edit_date()}]'
                )

                for item in geeklist.filter(("thing", "boardgame")):
                    yield item.object_id()

                print(f"Finished GeekList {geeklist.id()}")

            elif user_input.isdigit():
                yield int(user_input)

            else:
                yield self.__get_game_id_from_name(user_input)

    @staticmethod
    def __get_game_id_from_name(user_input: str) -> int:
        results = RequestSearch().ofType("boardgame").query(user_input)
        result = firstx(results)
        if len(results) == 1:
            print(f"Game found (as '{result.name()[0]}')")
        else:
            print(
                f"More than one entry found, using '{result.name()[0]}' published in {result.yearPublished()}"
            )
        return result.id()
