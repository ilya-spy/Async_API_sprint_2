from dataclasses import dataclass
from typing import Generator

from asyncpg.connection import Connection

from etl.models import Message

from .base import BaseEnricher


@dataclass
class Film(BaseEnricher):
    """Получает из бд полные данные по фильму."""

    async def fill_model(self, conn: Connection, messages: list[Message]) -> Generator[Message, None, None]:
        """Возвращает сообщение с найденной моделью фильма.

        :param conn:
        :param messages:
        :rtype: Generator[Message, None, None]
        """
        sql = '''
            SELECT
                fw.id,
                fw.type,
                fw.title,
                fw.description,
                fw.rating,
                COALESCE (
                    json_agg(
                       DISTINCT jsonb_build_object(
                           'id', p.id,
                           'role', pfw.role,
                           'full_name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
                ) as persons,
                COALESCE (
                    json_agg(
                       DISTINCT jsonb_build_object(
                           'id', g.id,
                           'name', g.name 
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
                ) as genres
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
            LEFT JOIN genre g on g.id = gfw.genre_id
            LEFT JOIN person_film_work pfw on fw.id = pfw.film_work_id
            LEFT JOIN person p on p.id = pfw.person_id
            WHERE fw.id = ANY(%s)
            GROUP BY fw.id
        '''
        ids = [message.obj_id for message in messages]
        async with conn.transaction():
            async for row in conn.cursor(sql, ids, prefetch=self.chunk_size):
                yield Film(**row)
