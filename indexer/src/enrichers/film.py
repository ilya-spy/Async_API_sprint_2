from dataclasses import dataclass

from asyncpg.connection import Connection
from entities.film import Film
from message import Message
from pydantic import BaseModel

from .base import BaseEnricher


@dataclass
class FilmEnricher(BaseEnricher):
    """Получает из бд полные данные по фильму."""

    async def retrieve_models(self, conn: Connection, messages: list[Message]) -> dict[str, BaseModel]:
        """Получает из бд фильмы и сохраняет в сообщение.

        :param conn:
        :param messages:
        :rtype: dict[str, BaseModel]
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
            WHERE fw.id = ANY($1)
            GROUP BY fw.id
        '''

        ids = [m.obj_id for m in messages]
        film_map = dict()
        async with conn.transaction():
            async for row in conn.cursor(sql, ids, prefetch=self.chunk_size):
                film_map[row['id']] = Film(**row)
        return film_map
