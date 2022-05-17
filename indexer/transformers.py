from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel

import documents
import models


@dataclass
class Base(metaclass=ABCMeta):
    """Базовый класс для преобразователей."""

    @abstractmethod
    def transform(self, items: list[BaseModel]) -> list[BaseModel]:
        """

        :param items:
        :return:
        """
        pass


@dataclass
class ElasticSearchMovie(Base):

    def transform(self, items: list[models.Movie]) -> list[documents.Movie]:
        """Преобразует список моделей бд в список документов elasticsearch.

        :param items:
        :return:
        """
        return [self.map(item) for item in items]

    def map(self, item: models.Movie) -> documents.Movie:
        """Преобразует модель бд в документ elasticsearch.

        :param item:
        :return:
        """
        return documents.Movie(
            id=item.id,
            type=item.type,
            imdb_rating=item.rating,
            title=item.title,
            description=item.description,
            genre=[documents.Genre(**genre.dict()) for genre in item.genres],
            directors=self.get_person(item.persons, models.RoleEnum.director),
            actors=self.get_person(item.persons, models.RoleEnum.actor),
            writers=self.get_person(item.persons, models.RoleEnum.writer),
        )

    @staticmethod
    def get_person(persons: list[models.Person], role: models.RoleEnum) -> list[documents.Person]:
        """Фильтрует список персон по роли и возвращает список документов для elasticsearch.

        :param persons:
        :param role:
        :return:
        """
        return [documents.Person(id=person.id, full_name=person.full_name)
                for person in persons
                if person.role == role]
