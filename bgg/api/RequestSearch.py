import time
import xml.etree.ElementTree as ET
from typing import Dict, Optional

import requests

from ..model.Items import Items
from ..utils import nonthrows

BASE_URL = "https://www.boardgamegeek.com/xmlapi2/"

# Each page in the API responses contains up to 100 entries.
ENTRIES_IN_FULL_PAGE = 100

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429

MAX_RETRIES = 5


class RequestSearch:
    """
    A request for a list of items resulting from searching
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API2#toc14
    """

    __type: Optional[str]

    def __init__(self):
        self.__type = None

    def ofType(self, type: str) -> "RequestSearch":
        self.__type = type
        return self

    def query(self, query: str, is_exact: bool = True) -> Items:
        uri = f"{BASE_URL}search"
        params = self.__getParams()
        params["query"] = query
        if is_exact:
            params["exact"] = "1"

        for retries in range(MAX_RETRIES):
            response = requests.get(uri, params=params)
            root = ET.fromstring(response.text)

            if response.status_code == HTTP_STATUS_CODE_OK:
                print(f"Search results for {query} received")
                results = Items(root)
                return results

            elif response.status_code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS:
                if root.tag != "error":
                    raise Exception(
                        f"Unexpected error format, was exepecting 'error' tag but got {root.tag}"
                    )
                message = nonthrows(root.find("message")).text
                retry_secs = 2 ** (retries)  # Exponential backoff
                print(f'TOO MANY REQUESTS["{message}"]. Retrying in {retry_secs}s')
                time.sleep(retry_secs)

            else:
                raise Exception(f"Bad API response: {response.status_code}")

        raise Exception(
            f"Bailing out! failed to query server for query {query} after {retries} retries"
        )

    def __getParams(self) -> Dict[str, str]:
        params = {}

        if self.__type:
            params["type"] = self.__type

        return params
