import asyncio
from abc import ABC, abstractmethod
from logging import Logger

_PINGS_TO_NOTIFY = 30


class ConnectChecker(ABC):
    @abstractmethod
    async def ping(self) -> bool:
        pass


async def wait(conn: ConnectChecker, logger: Logger, ping_to_notify: int = _PINGS_TO_NOTIFY):
    logger.info(f"Try to connect to {conn}.")
    cnt = 0
    while not await conn.ping():
        await asyncio.sleep(1)
        cnt += 1
        if cnt > ping_to_notify:
            logger.warning(f"{conn} no responses for pings.")
            cnt = 0
    logger.info(f"{conn} is ready for work.")
