import abc
import bz2
import os
import tempfile
import time
import xml.etree.ElementTree as ET
from typing import IO, Dict, Generic, Optional, Tuple, TypeVar

import requests

from ..utils import InlineOutput, nonthrows

API_BASE_URL = {
    1: "https://www.boardgamegeek.com/xmlapi",
    2: "https://www.boardgamegeek.com/xmlapi2",
}


HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429
HTTP_STATUS_CODE_BAD_GATEWAY = 502

MAX_RETRIES = 5

CACHE_ROOT_DIR = "bggcache"

TResponse = TypeVar("TResponse")


class RequestBase(Generic[TResponse]):
    def _cache_dir(self) -> Optional[str]:
        return None

    @abc.abstractmethod
    def _api_version(self) -> int:
        pass

    @abc.abstractmethod
    def _cache_file_name(str, **kwargs) -> str:
        pass

    @abc.abstractmethod
    def _api_path(self, **kwargs) -> str:
        pass

    @abc.abstractmethod
    def _api_params(self, **kwargs) -> Dict[str, str]:
        pass

    @abc.abstractmethod
    def _build_response(self, root: ET.Element) -> TResponse:
        pass

    def _fetch(self, **kwargs) -> TResponse:
        for retries in range(MAX_RETRIES):
            page_contents, status_code = self.__getRawResponse(**kwargs)

            if status_code == HTTP_STATUS_CODE_BAD_GATEWAY:
                retry_secs = 0.75 * (2 ** retries)  # Exponential backoff
                InlineOutput.write(f" BAD GATEWAY! Retrying in {retry_secs}s")
                time.sleep(retry_secs)
                continue

            try:
                root = ET.fromstring(page_contents)
                if status_code == HTTP_STATUS_CODE_OK:
                    return self._build_response(root)

                elif status_code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS:
                    if root.tag != "error":
                        raise Exception(
                            f"Unexpected error format, was exepecting 'error' tag but got {root.tag}"
                        )
                    message = nonthrows(root.find("message")).text
                    retry_secs = 0.75 * (2 ** retries)  # Exponential backoff
                    InlineOutput.write(
                        f' TOO MANY REQUESTS["{message}"]. Retrying in {retry_secs}s'
                    )
                    time.sleep(retry_secs)

                else:
                    raise Exception(f"Bad API response: {status_code}")

            except ET.ParseError as e:
                InlineOutput.overwrite(
                    f"Couldn't parse response with code: {status_code} [{e.msg}]. Contents:\n{page_contents}"
                )

        raise Exception(f"Bailing out! API FETCH failed {retries} retries")

    def __getRawResponse(self, **kwargs) -> Tuple[str, int]:
        cached = self.__readFromCache(**kwargs)
        if cached:
            return cached, HTTP_STATUS_CODE_OK

        uri = f"{API_BASE_URL[self._api_version()]}/{self._api_path(**kwargs)}"
        response = requests.get(uri, params=self._api_params(**kwargs))
        response_text = response.text
        if response.status_code == HTTP_STATUS_CODE_OK:
            self.__writeToCache(response_text, **kwargs)
        return response_text, response.status_code

    def __openCacheFile(self, mode: str, **kwargs) -> IO:
        cache_dir = self.__getCacheRootDir()
        if mode == "w":
            # Create the directory if it doesnt exist before opening the file
            # for writing
            os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(
            cache_dir, f"{self._cache_file_name(**kwargs)}.xml.bz2"
        )
        return bz2.open(cache_file, f"{mode}t")

    def __readFromCache(self, **kwargs) -> Optional[str]:
        try:
            with self.__openCacheFile("r", **kwargs) as cache:
                return cache.read()
        except FileNotFoundError:
            return None

    def __writeToCache(self, response: str, **kwargs) -> None:
        with self.__openCacheFile("w", **kwargs) as cache:
            cache.write(response)

    def __getCacheRootDir(self) -> str:
        parts = [tempfile.gettempdir(), CACHE_ROOT_DIR, self.__class__.__name__]
        cache_dir = self._cache_dir()
        if cache_dir:
            parts.append(cache_dir)
        return os.path.join(*parts)
