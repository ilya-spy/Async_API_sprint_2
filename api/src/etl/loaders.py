import asyncio
import logging
from abc import ABCMeta, abstractmethod
from asyncio import AbstractEventLoop, Queue
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Generator

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from etl.state import State
from etl.transformers import BaseTransformer
from etl.utils import backoff


@dataclass
class BaseLoader(metaclass=ABCMeta):
    """Базовый класс для загрузчиков"""

    @abstractmethod
    async def load(self, loop: AbstractEventLoop, pool: ProcessPoolExecutor, queue: Queue):
        """Загружает документы в хранилище

        :param loop:
        :param pool:
        :param queue:
        :return:
        """
        pass


@dataclass
class ElasticIndex(BaseLoader):
    """Загрузчик фильмов в elasticsearch."""

    elastic: AsyncElasticsearch
    transformer: BaseTransformer
    index_name: str
    state: State
    logger: logging.Logger

    @backoff()
    async def load(self, loop: AbstractEventLoop, pool: ProcessPoolExecutor, queue: Queue):
        """Загружает документы в хранилище

        :param loop:
        :param pool:
        :param queue:
        :return:
        """
        batch = []
        task_set = set()
        while True:
            message = queue.get()
            if message is not None:
                batch.append(message)
            if queue.empty():
                task = loop.run_in_executor(pool, self.transformer.transform, batch)
                task_set.add(task)
                if len(task_set) >= pool._max_workers:
                    done_set, task_set = await asyncio.wait(
                        task_set, return_when=asyncio.FIRST_COMPLETED
                    )
                    await
                batch = []
            if message is None:
                break
        success, failed = await async_bulk(self.elastic, index=self.index_name, actions=self.generate_actions(items))
        if success:
            self.update_last_modified
        return success

    async def task_set_load_helper(self, task_set: set, connection):
        for future in task_set:
            await self.load(await future, connection)

    @staticmethod
    def generate_actions(message: list[documents.Movie]) -> Generator[dict, None, None]:
        """Генерирует объекты запроса для сохранения в elasticsearch.

        :param items:
        :return:
        """
        for item in items:
            yield dict(
                _id=item.id,
                _source=item.dict(),
            )
