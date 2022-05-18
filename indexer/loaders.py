from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Generator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import documents
from utils import backoff


@dataclass
class Base(metaclass=ABCMeta):
    """Базовый класс для загрузчиков"""

    @abstractmethod
    def load(self, items: list[Any]) -> int:
        """Загружает документы в хранилище

        :return:
        """
        pass


@dataclass
class ElasticSearchMovie(Base):
    """Загрузчик фильмов в elasticsearch."""

    client: Elasticsearch
    index: str

    @backoff()
    def load(self, items: list[documents.Movie]) -> int:
        """Загружает документы в хранилище

        :return:
        """
        success, failed = bulk(self.client, index=self.index, actions=self.generate_actions(items))
        return success

    @staticmethod
    def generate_actions(items: list[documents.Movie]) -> Generator[dict, None, None]:
        """Генерирует объекты запроса для сохранения в elasticsearch.

        :param items:
        :return:
        """
        for item in items:
            yield dict(
                _id=item.id,
                _source=item.dict(),
            )
