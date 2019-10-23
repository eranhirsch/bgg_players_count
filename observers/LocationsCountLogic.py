import re
from typing import Dict

from bgg.model.Play import Play

# A list of apps and platforms that allow digital play. KEEP LOWERCASE!
DIGITAL_LOCATIONS_RE = [
    re.compile(re_str, re.IGNORECASE)
    for re_str in [
        r"(\w+\.)?isotropic(\.org)?",
        r"a smartphone",
        r"app",
        r"b(oard)? ?g(ame)? ?a(rena)?(\.com)?",
        r"emulator",
        r"internet",
        r"iphone",
        r"online",
        r"pc",
        r"steam",
        r"tabletop simulator",
        r"web",
    ]
]


class LocationsCountLogic:
    __locations: Dict[str, int] = {}

    def visit(self, play: Play):
        location = play.location()
        if not location:
            return

        if any([re.match(location) for re in DIGITAL_LOCATIONS_RE]):
            return

        location = location.lower()
        try:
            self.__locations[location] += 1
        except KeyError:
            self.__locations[location] = 1

    def getResults(self) -> Dict[str, int]:
        return self.__locations
