import asyncio
import logging

from functools import wraps
from abc import ABC, abstractmethod
from logging import Logger


logger = logging.getLogger(__name__)


def backoff(service_name, start_sleep_time=0.1, factor=2, border_sleep_time=20):
    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            time_sleep, n = 0, 0
            while True:
                try:
                    logger.info(f"### Backoff: attempt to run {service_name} #" + str(n + 1))
                    await asyncio.sleep(time_sleep)
                    await func(*args, **kwargs)
                except KeyboardInterrupt:
                    logger.error("### Backoff: procedure terminated forcedly")
                    break
                except Exception as ex:
                    logger.error(f"### Backoff: exception retrying:\n{service_name}\n{ex}")
                else:
                    logger.info(f"{service_name} is ready for work.")
                    return

                time_sleep = (
                    start_sleep_time * factor ** n
                    if time_sleep < border_sleep_time
                    else border_sleep_time
                )
                n += 1
                if n > ConnectChecker.RETRY_ATTEMPTS:
                    logger.info("### Backoff: retry limit reached. Bail out...")
                    return
        return wrapper

    return decorator


class ConnectChecker(ABC):
    RETRY_ATTEMPTS = 30

    def __init__(self, logger) -> None:
        self.logger: Logger = logger

    @abstractmethod
    async def ping(self) -> bool:
        pass
