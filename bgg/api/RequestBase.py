import abc
import bz2
import os
import tempfile
import time
import xml.etree.ElementTree as ET
from typing import IO, Dict, Generic, Optional, TypeVar

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
    @abc.abstractmethod
    def _api_version(self) -> int:
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

    def _cache_dir(self) -> Optional[str]:
        return None

    @abc.abstractmethod
    def _cache_file_name(str, **kwargs) -> str:
        pass

    def _fetch(self, **kwargs) -> TResponse:
        for retries in range(MAX_RETRIES):
            try:
                page_contents = self.__getRawResponse(**kwargs)
                root = ET.fromstring(page_contents)
                return self._build_response(root)
            except ServerIssue as issue:
                InlineOutput.write(
                    f" Encountered server issue {issue.tldr}: {issue.extra or ''}"
                )
            except ET.ParseError as e:
                InlineOutput.overwrite(
                    f"Failed to parse response [{e.msg}]. Contents:\n{page_contents}"
                )

            retry_secs = 0.75 * (2 ** retries)  # Exponential backoff
            InlineOutput.write(f" Retrying in {retry_secs}s")
            time.sleep(retry_secs)

        raise Exception(f"Bailing out! API FETCH failed {MAX_RETRIES} retries")

    def __getRawResponse(self, **kwargs) -> str:
        cached = self.__readFromCache(**kwargs)
        if cached:
            return cached

        uri = f"{API_BASE_URL[self._api_version()]}/{self._api_path(**kwargs)}"
        response = requests.get(uri, params=self._api_params(**kwargs))

        if response.status_code == HTTP_STATUS_CODE_OK:
            self.__writeToCache(response.text, **kwargs)
            return response.text

        if response.status_code == HTTP_STATUS_CODE_BAD_GATEWAY:
            raise ServerIssue("BAD GATEWAY")

        if response.status_code == HTTP_STATUS_CODE_TOO_MANY_REQUESTS:
            # Rate limiting responses are returned as XMLs with an error message
            error = ET.fromstring(response.text)
            raise ServerIssue(
                "RATE LIMITED",
                nonthrows(error.find("message")).text
                if error.tag == "error"
                else "Failed to parse error message!",
            )

        raise ServerIssue(
            "UNEXPECTED STATUS CODE", f"Status code: {response.status_code}"
        )

    def __readFromCache(self, **kwargs) -> Optional[str]:
        try:
            with self.__openCacheFile("r", **kwargs) as cache:
                return cache.read()
        except FileNotFoundError:
            return None

    def __writeToCache(self, response: str, **kwargs) -> None:
        with self.__openCacheFile("w", **kwargs) as cache:
            cache.write(response)

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

    def __getCacheRootDir(self) -> str:
        parts = [tempfile.gettempdir(), CACHE_ROOT_DIR, self.__class__.__name__]
        cache_dir = self._cache_dir()
        if cache_dir:
            parts.append(cache_dir)
        return os.path.join(*parts)


class ServerIssue(Exception):
    def __init__(self, tldr: str, extra: Optional[str] = None) -> None:
        self.tldr = tldr
        self.extra = extra
