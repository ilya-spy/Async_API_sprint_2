from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel

import etl.models as postgres
import models as elasctic


@dataclass
class BaseTransformer(metaclass=ABCMeta):
    """Базовый класс для преобразователей."""

    @abstractmethod
    def transform(self, items: list[BaseModel]) -> list[BaseModel]:
        """

        :param items:
        :return:
        """
        pass


@dataclass
class PgFilmToElasticSearch(BaseTransformer):

    def transform(self, items: list[postgres.Film]) -> list[elasctic.Film]:
        """Преобразует список моделей бд в список документов elasticsearch.

        :param items:
        :return:
        """
        return [self.map(item) for item in items]

    def map(self, item: postgres.Film) -> elasctic.Film:
        """Преобразует модель бд в документ elasticsearch.

        :param item:
        :return:
        """
        return elasctic.Film(
            id=item.id,
            type=item.type,
            imdb_rating=item.rating,
            title=item.title,
            description=item.description,
            genre=[elasctic.Genre(**genre.dict()) for genre in item.genres],
            directors=self.get_person(item.persons, postgres.RoleEnum.director),
            actors=self.get_person(item.persons, postgres.RoleEnum.actor),
            writers=self.get_person(item.persons, postgres.RoleEnum.writer),
        )

    @staticmethod
    def get_person(persons: list[postgres.Person], role: postgres.RoleEnum) -> list[elasctic.Person]:
        """Фильтрует список персон по роли и возвращает список документов для elasticsearch.

        :param persons:
        :param role:
        :return:
        """
        return [elasctic.Person(id=person.id, full_name=person.full_name)
                for person in persons
                if person.role == role]
