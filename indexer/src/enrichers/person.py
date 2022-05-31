from dataclasses import dataclass

from asyncpg.connection import Connection
from entities.person import Person
from message import Message
from pydantic import BaseModel

from .base import BaseEnricher


@dataclass
class PersonEnricher(BaseEnricher):
    """Получает из бд полные данные по персоне."""

    async def retrieve_models(self, conn: Connection, messages: list[Message]) -> dict[str, BaseModel]:
        """Получает из бд персон и сохраняет в сообщение.

        :param conn:
        :param messages:
        :rtype: dict[str, BaseModel]
        """
        sql = '''
            SELECT
                p.id,
                p.full_name,
                COALESCE (
                    json_agg(
                       DISTINCT jsonb_build_object(
                           'film_id', fw.id,
                           'role', pfw.role,
                           'title', fw.title
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
                ) as films
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON pfw.person_id =  p.id
            LEFT JOIN content.film_work fw on fw.id = pfw.film_work_id
            WHERE p.id = ANY($1)
            GROUP BY p.id
        '''

        ids = [m.obj_id for m in messages]
        person_map = dict()
        async with conn.transaction():
            async for row in conn.cursor(sql, ids, prefetch=self.chunk_size):
                person_map[row['id']] = Person(**row)
        return person_map
