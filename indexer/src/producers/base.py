import asyncio
import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

import state
from db import postgres
from helpers import get_last_modified
from message import Message


@dataclass
class BaseProducer(metaclass=ABCMeta):
    """Базовый класс для продьюсеров получающих данные из postgres"""
    db: postgres.DB
    check_interval: float
    chunk_size: int
    state: state.State
    logger: logging.Logger

    conn: object = field(default=None)

    async def produce(self, queue: asyncio.Queue) -> None:
        """ В бесконечном цикле выполняет запросы к бд и отправляет найденные измененные записи в очередь.
        Запросы выполняются каждые check_interval секунд.

        :param queue:
        :rtype: None
        """
        self.conn = await self.db.get_connection()
        self.logger.info('Established new DB connection')
        try:
            while True:
                # need to advance last modified only when confirmed from loader through State
                # otherwise failures in elastic loader don't have feedback for producer
                last_modified = await get_last_modified(self.state, self.__class__.__name__)
                # since last confirmed update
                total_produced = 0
                async with self.conn.transaction():
                    async for row in self.conn.cursor(self.sql(), last_modified, prefetch=self.chunk_size):
                        await queue.put(Message(
                            producer_name=self.__class__.__name__,
                            obj_id=row['id'],
                            obj_modified=row['modified'],
                        ))
                        last_modified = max(last_modified, row['modified'])
                        total_produced += 1
                self.logger.debug(f'Items produced: {total_produced}')
                await asyncio.sleep(self.check_interval)
        finally:
            self.release()

    async def release(self):
        await self.conn.close()
        self.logger.info('DB connection closed')

    @abstractmethod
    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        pass
