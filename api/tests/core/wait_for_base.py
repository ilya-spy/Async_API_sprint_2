import asyncio
from abc import ABC, abstractmethod
from logging import Logger


class ConnectChecker(ABC):
    RETRY_ATTEMPTS = 30

    def __init__(self, logger) -> None:
        self.logger: Logger = logger

    @abstractmethod
    async def ping(self) -> bool:
        pass

    async def wait(self):
        self.logger.info(f"Try to connect to {self}.")
        cnt = 0
        while not await self.ping():
            await asyncio.sleep(1)
            cnt += 1
            if cnt > ConnectChecker.RETRY_ATTEMPTS:
                self.logger.warning(f"{self} no responses for pings.")
                cnt = 0
        self.logger.info(f"{self} is ready for work.")
