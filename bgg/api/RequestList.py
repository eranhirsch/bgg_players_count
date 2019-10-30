import time
import xml.etree.ElementTree as ET
from typing import Dict

import requests

from ..model.GeekList import GeekList
from ..utils import nonthrows

BASE_URL = "https://www.boardgamegeek.com/xmlapi/"

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429

MAX_RETRIES = 5


class RequestList:
    """
    A request for a geek list of items
    Defined in: https://boardgamegeek.com/wiki/page/BGG_XML_API#toc7
    """

    def __init__(self, listid: int) -> None:
        self.__listID = listid

    def fetch(self, with_comments: bool = False) -> GeekList:
        uri = f"{BASE_URL}geeklist/{self.__listID}"
        params: Dict[str, str] = {}
        if with_comments:
            params["comments"] = "1"

        for retries in range(MAX_RETRIES):
            response = requests.get(uri, params=params)
            root = ET.fromstring(response.text)

            if response.status_code == HTTP_STATUS_CODE_OK:
                print(f"Geeklist found!")
                results = GeekList(root)
                return results

            elif response.status_code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS:
                if root.tag != "error":
                    raise Exception(
                        f"Unexpected error format, was exepecting 'error' tag but got {root.tag}"
                    )
                message = nonthrows(root.find("message")).text
                retry_secs = 0.75 ** (retries)  # Exponential backoff
                print(f'TOO MANY REQUESTS["{message}"]. Retrying in {retry_secs}s')
                time.sleep(retry_secs)

            else:
                raise Exception(f"Bad API response: {response.status_code}")

        raise Exception(
            f"Bailing out! failed to fetch geeklist {self.__listID} after {retries} retries"
        )
