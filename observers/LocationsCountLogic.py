import re
from typing import Dict

from bgg.model.Play import Play

# A list of apps and platforms that allow digital play. KEEP LOWERCASE!
DIGITAL_LOCATIONS_RE = [
    re.compile(re_str)
    for re_str in [
        r"(\w+\.)?isotropic(\.org)?",
        r"a smartphone",
        r"b(oard)? ?g(ame)? ?a(rena)?(\.com)?",
        r"emulator",
        r"online",
        r"tabletop simulator",
    ]
]


class LocationsCountLogic:
    __locations: Dict[str, int] = {}

    def visit(self, play: Play):
        location = play.location()
        if location:
            location = location.lower()
            if not any([re.match(location) for re in DIGITAL_LOCATIONS_RE]):
                try:
                    self.__locations[location] += 1
                except KeyError:
                    self.__locations[location] = 1

    def getResults(self) -> Dict[str, int]:
        return self.__locations
