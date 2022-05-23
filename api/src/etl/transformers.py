from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generator

import etl.entities as postgres
from etl.entities import Message
from models import film, genre, person


@dataclass
class BaseTransformer(metaclass=ABCMeta):
    """Базовый класс для преобразователей."""

    @abstractmethod
    async def transform(self, messages: list[Message]) -> list[Message]:
        """Абстрактный метод преобразования сообщений.

        :param messages:
        :return:
        """
        pass


@dataclass
class PgFilmToElasticSearch(BaseTransformer):

    async def transform(self, messages: list[Message]) -> list[Message]:
        """Преобразует список моделей бд в список документов elasticsearch.

        :param messages:
        :return:
        """
        return [self.map(m) for m in messages]

    def map(self, message: Message) -> Message:
        """Преобразует модель бд в документ elasticsearch.

        :param message:
        :rtype: Message
        """
        item = postgres.Film(**message.obj_model.dict())
        message.obj_model = film.Film(
            id=item.id,
            type=item.type,
            imdb_rating=item.rating,
            title=item.title,
            description=item.description,
            genre=[genre.Genre(**g.dict()) for g in item.genres],
            directors=self.get_person(item.persons, postgres.RoleEnum.director),
            actors=self.get_person(item.persons, postgres.RoleEnum.actor),
            writers=self.get_person(item.persons, postgres.RoleEnum.writer),
        )
        return message

    @staticmethod
    def get_person(persons: list[postgres.Person], role: postgres.RoleEnum) -> list[person.Person]:
        """Фильтрует список персон по роли и возвращает список документов для elasticsearch.

        :param persons:
        :param role:
        :return:
        """
        return [person.Person(id=p.id, full_name=p.full_name)
                for p in persons
                if p.role == role]
