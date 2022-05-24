import asyncio
import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from db import postgres
from etl import entities, state
from etl.helpers import get_last_modified


@dataclass
class BaseProducer(metaclass=ABCMeta):
    """Базовый класс для продьюсеров получающих данные из postgres"""

    db: postgres.DB
    check_interval: float
    chunk_size: int
    state: state.State
    logger: logging.Logger

    async def produce(self, queue: asyncio.Queue) -> None:
        """ В бесконечном цикле выполняет запросы к бд и отправляет найденные измененные записи в очередь.
        Запросы выполняются каждые check_interval секунд.

        :param queue:
        :rtype: None
        """
        conn = await self.db.get_connection()
        try:
            last_modified = await get_last_modified(self.state, self.__class__.__name__)
            while True:
                async with conn.transaction():
                    async for row in conn.cursor(self.sql(), last_modified, prefetch=self.chunk_size):
                        await queue.put(entities.Message(
                            producer_name=self.__class__.__name__,
                            obj_id=row['id'],
                            obj_modified=row['modified'],
                        ))
                        last_modified = max(last_modified, row['modified'])
                await asyncio.sleep(self.check_interval)
        finally:
            await conn.close()

    @abstractmethod
    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        pass


class FilmworkPersonModified(BaseProducer):
    """Находит все фильмы, в которых приняли участие персоны, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql.

        :rtype: str
        """
        return '''
            SELECT pfw.film_work_id as id, p.modified 
            FROM content.person p 
            INNER JOIN content.person_film_work pfw ON pfw.person_id = p.id
            WHERE p.modified > $1 
            ORDER BY p.modified DESC
        '''


class FilmworkGenreModified(BaseProducer):
    """Находит все фильмы с жанром, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT gfw.film_work_id as id, g.modified 
            FROM content.genre g 
            INNER JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
            WHERE g.modified > $1
            ORDER BY g.modified DESC
        '''


class FilmworkModified(BaseProducer):
    """Находит все фильмы, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT id, modified 
            FROM content.film_work
            WHERE modified > $1
            ORDER BY modified DESC
        '''


class GenreModified(BaseProducer):
    """Находит все жанры, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT g.id as id, g.modified
            FROM content.genre g 
            WHERE g.modified > $1
            ORDER BY g.modified DESC
        '''

class PersonModified(BaseProducer):
    """Находит всех персон, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT p.id as id, p.modified
            FROM content.person p
            WHERE p.modified > $1
            ORDER BY p.modified DESC
        '''
