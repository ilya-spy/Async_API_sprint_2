from abc import ABCMeta, abstractmethod
from asyncio import Queue
from dataclasses import dataclass
from typing import Generator

from asyncpg.connection import Connection

from db import postgres
from etl.models import Message
from etl.utils import backoff


@dataclass
class BaseEnricher(metaclass=ABCMeta):
    """Базовый класс обогатителя."""
    db: postgres.DB
    max_batch_size: int
    chunk_size: int

    @backoff()
    async def enrich(self, producer_queue: Queue, loader_queue: Queue) -> None:
        conn = self.db.get_connection()
        batch = []
        try:
            while True:
                message = await producer_queue.get()
                if message is not None:
                    batch.append(message)
                if batch and (len(batch) >= self.max_batch_size or producer_queue.empty()):
                    async for enriched_message in self.fill_model(conn, batch):
                        await loader_queue.put(enriched_message)
                    batch = []
                if message is None:
                    break
        finally:
            await conn.close()

    @abstractmethod
    async def fill_model(self, conn: Connection, messages: list[Message]) -> Generator[Message, None, None]:
        pass
