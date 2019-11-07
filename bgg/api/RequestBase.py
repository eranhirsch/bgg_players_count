import abc
import bz2
import datetime
import os
import time
import xml.etree.ElementTree as ET
from enum import IntEnum
from typing import IO, Dict, Generic, Iterator, Optional, TypeVar

import requests

from ..utils import InlineOutput, nonthrows
from .RateLimiter import RateLimiter

API_BASE_URL = {
    # Docs: https://boardgamegeek.com/wiki/page/BGG_XML_API
    1: "https://www.boardgamegeek.com/xmlapi",
    # Docs: https://boardgamegeek.com/wiki/page/BGG_XML_API2
    2: "https://www.boardgamegeek.com/xmlapi2",
}


class HttpStatusCode(IntEnum):
    OK = 200
    TOO_MANY_REQUESTS = 429
    BAD_GATEWAY = 502


MAX_RETRIES = 5
RETRY_BASE_INTERVAL = datetime.timedelta(seconds=1)

# A real temp dir can be found here: tempfile.gettempdir(), but this gets
# deleted too to be reliable for what I need of it right now...
TEMP_ROOT_DIR = ".tmp"
CACHE_ROOT_DIR = "bggcache"

TResponse = TypeVar("TResponse")


class RequestBase(Generic[TResponse]):

    __rate_limiter = RateLimiter()

    @classmethod
    def cached_queries(cls) -> Iterator[str]:
        dir = cls.__getRequestTypeCacheRootDir()
        for id in os.listdir(dir):
            yield id

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

            retry_secs = RETRY_BASE_INTERVAL * (2 ** retries)  # Exponential backoff
            InlineOutput.write(f" Retrying in {retry_secs}s")
            time.sleep(retry_secs.total_seconds())

        raise Exception(f"Bailing out! API FETCH failed {MAX_RETRIES} retries")

    def __getRawResponse(self, **kwargs) -> str:
        cached = self.__readFromCache(**kwargs)
        if cached:
            return cached

        uri = f"{API_BASE_URL[self._api_version()]}/{self._api_path(**kwargs)}"
        RequestBase.__rate_limiter.limit()
        response = requests.get(uri, params=self._api_params(**kwargs))

        if response.status_code == HttpStatusCode.OK:
            RequestBase.__rate_limiter.success()
            self.__writeToCache(response.text, **kwargs)
            return response.text

        if response.status_code == HttpStatusCode.BAD_GATEWAY:
            raise ServerIssue("BAD GATEWAY")

        if response.status_code == HttpStatusCode.TOO_MANY_REQUESTS:
            RequestBase.__rate_limiter.fail()

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
        cache_dir = self.__getInstanceCacheRootDir()
        if mode == "w":
            # Create the directory if it doesnt exist before opening the file
            # for writing
            os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(
            cache_dir, f"{self._cache_file_name(**kwargs)}.xml.bz2"
        )
        return bz2.open(cache_file, f"{mode}t")

    def __getInstanceCacheRootDir(self) -> str:
        request_root_dir = self.__getRequestTypeCacheRootDir()
        cache_dir = self._cache_dir()
        if not cache_dir:
            return request_root_dir

        return os.path.join(request_root_dir, cache_dir)

    @classmethod
    def __getRequestTypeCacheRootDir(cls) -> str:
        return os.path.join(TEMP_ROOT_DIR, CACHE_ROOT_DIR, cls.__name__)


class ServerIssue(Exception):
    def __init__(self, tldr: str, extra: Optional[str] = None) -> None:
        self.tldr = tldr
        self.extra = extra
