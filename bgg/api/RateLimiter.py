import datetime
import time
from typing import Optional

INITIAL_UPPER_BOUND = datetime.timedelta(seconds=10)

SUCCESS_BUMP = 10

class RateLimiter:
    def __init__(self) -> None:
        self.__last_attempt_time: Optional[datetime.datetime] = None
        self.__lower_bound: datetime.timedelta = datetime.timedelta(seconds=0)
        self.__upper_bound: datetime.timedelta = datetime.timedelta(seconds=0)
        self.__successive_successes: int = 0

    def limit(self) -> None:
        delay_time = self.__delay_time()
        if delay_time and self.__last_attempt_time:
            elapsed = datetime.datetime.now() - self.__last_attempt_time
            remaining = delay_time - elapsed
            if remaining.total_seconds() > 0:
                time.sleep(remaining.total_seconds())
        self.__last_attempt_time = datetime.datetime.now()

    def success(self) -> None:
        self.__successive_successes += 1
        if self.__successive_successes >= SUCCESS_BUMP:
            self.__successive_successes = 0
            self.__upper_bound = self.__delay_time()

    def fail(self) -> None:
        self.__successive_successes = 0
        self.__last_attempt_time = None
        if not self.__upper_bound:
            self.__upper_bound = INITIAL_UPPER_BOUND
        else:
            self.__lower_bound = self.__delay_time()

    def __delay_time(self) -> datetime.timedelta:
        return (self.__lower_bound + self.__upper_bound) / 2
