import logging
from abc import ABCMeta, abstractmethod
from asyncio import Queue
from dataclasses import dataclass

from asyncpg.connection import Connection
from pydantic import BaseModel

from db import postgres
from etl.entities import Message


@dataclass
class BaseEnricher(metaclass=ABCMeta):
    """Базовый класс обогатителя."""
    db: postgres.DB
    logger: logging.Logger
    max_batch_size: int
    chunk_size: int

    async def enrich(self, producer_queue: Queue, loader_queue: Queue) -> None:
        conn = await self.db.get_connection()
        batch = []
        total_enriched = 0
        try:
            while True:
                message = await producer_queue.get()
                if message is not None:
                    batch.append(message)
                if batch and (len(batch) >= self.max_batch_size or producer_queue.empty()):
                    models_map = await self.retrieve_models(conn, batch)
                    for message in batch:
                        message.obj_model = models_map[message.obj_id]
                        await loader_queue.put(message)
                        total_enriched += 1
                    batch = []
                    self.logger.debug(f'Items enriched: {total_enriched}')
                    total_enriched = 0
                if message is None:
                    break
        finally:
            await conn.close()

    @abstractmethod
    async def retrieve_models(self, conn: Connection, messages: list[Message]) -> dict[str, BaseModel]:
        pass
