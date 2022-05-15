from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generator, NewType
from uuid import UUID

from db import DB
from utils import backoff

Chunk = NewType('Chunk', list[tuple[UUID, datetime]])


@dataclass
class Base(metaclass=ABCMeta):
    """Базовый класс для продьюсеров получающих данные из postgres"""

    db: DB
    chunk_size: int

    @backoff()
    def produce(self, last_modified: datetime) -> Generator[Chunk, None, None]:
        """ Выполняет запрос к бд на получение айдишников фильмов, в которых внесены изменения

        :param last_modified:
        :return:
        """
        with self.db.cursor() as curs:
            curs.execute(self._sql(), (last_modified,))

            has_rows = True
            while has_rows:
                rows = curs.fetchmany(self.chunk_size)
                if rows:
                    yield rows
                else:
                    has_rows = False

    @abstractmethod
    def _sql(self) -> str:
        """Возвращает sql-запрос.

        :return:
        """
        pass


class PersonModified(Base):
    """Находит все фильмы, в которых приняли участие персоны, чьи данные изменились с последнего синка."""

    def _sql(self) -> str:
        """Возвращает sql.

        :return:
        """
        return '''
            SELECT pfw.film_work_id, p.modified FROM content.person p 
            INNER JOIN content.person_film_work pfw ON pfw.person_id = p.id
            WHERE p.modified > %s 
            ORDER BY p.modified DESC
        '''


class GenreModified(Base):
    """Находит все фильмы с жанром, чьи данные изменились с последнего синка."""

    def _sql(self) -> str:
        """Возвращает sql-запрос.

        :return:
        """
        return '''
            SELECT gfw.film_work_id, g.modified FROM content.genre g 
            INNER JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
            WHERE g.modified > %s 
            ORDER BY g.modified DESC
        '''


class FilmworkModified(Base):
    """Находит все фильмы, чьи данные изменились с последнего синка."""

    def _sql(self) -> str:
        """Возвращает sql-запрос.

        :return: str
        """
        return '''
            SELECT id, modified FROM content.film_work
            WHERE modified > %s 
            ORDER BY modified DESC
        '''
