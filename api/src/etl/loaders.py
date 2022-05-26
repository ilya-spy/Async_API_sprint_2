
import logging
from abc import ABCMeta, abstractmethod
from asyncio import Queue
from collections import Counter
from dataclasses import dataclass
from operator import attrgetter
from typing import Generator

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from etl.entities import Message
from etl.helpers import get_last_modified
from etl.state import State
from etl.transformers import BaseTransformer


@dataclass
class BaseLoader(metaclass=ABCMeta):
    """Базовый класс для загрузчиков"""

    @abstractmethod
    async def load(self, queue: Queue):
        """Загружает документы в хранилище

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
    chunk_size: int

    def __post_init__(self):
        self._loaded_counter = Counter()


    async def load(self, queue: Queue):
        """Загружает документы в хранилище

        :param queue:
        :return:
        """
        batch = []
        while True:
            message = await queue.get()
            if message is not None:
                batch.append(message)
            if queue.empty() or (batch and len(batch) >= self.chunk_size):
                await self._load(batch)
                self.logger.debug('Total loaded: %s', self._loaded_counter)
                batch = []
            if message is None:
                break


    async def _load(self, messages: list[Message]):
        transformed_messages = await self.transformer.transform(messages)
        success, failed = 0, 0

        self.logger.debug(
            f'Bulk index load: {self.index_name} {len(messages)} {transformed_messages[0]}')
        try:
            success, failed = await async_bulk(
                self.elastic,
                index=self.index_name,
                actions=self._generate_actions(transformed_messages),
            )
        except Exception as e:
            self.logger.debug('Failed to bulk load, Exception: ' + str(e))
            failed = len(messages)
        finally:
            self.logger.debug(f'Got {success}/{failed} response for bulk index')
            if failed:
                raise Exception('Got failed items on elastic bulk insert')

        await self._update_last_modified(transformed_messages)
        self._loaded_counter.update([msg.producer_name for msg in transformed_messages])


    async def _update_last_modified(self, messages: list[Message]) -> None:
        """Для каждого типа продьюсеров нужно отдельно апдейтить last_modified.

        :param messages:
        :return:
        """
        producer_names = set([message.producer_name for message in messages])
        for name in producer_names:
            message_with_max_modified = max(
                filter(
                    lambda m: m.producer_name == name,
                    messages,
                ),
                key=attrgetter('obj_modified'),
            )

            last_modified = await get_last_modified(self.state, name)
            last_modified = max(last_modified, message_with_max_modified.obj_modified)

            await self.state.save_state(name, last_modified.isoformat())


    @staticmethod
    def _generate_actions(messages: list[Message]) -> Generator[dict, None, None]:
        """Генерирует объекты запроса для сохранения в elasticsearch.

        :param messages:
        :return:
        """
        for message in messages:
            yield dict(
                _id=message.obj_id,
                _source=message.obj_model.dict(),
            )
