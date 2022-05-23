from dataclasses import dataclass

from asyncpg.connection import Connection
from pydantic import BaseModel

from etl.entities import Person, Message
from .base import BaseEnricher


@dataclass
class PersonEnricher(BaseEnricher):
    """Получает из бд полные данные по персоне."""

    async def retrieve_models(self, conn: Connection,
                              messages: list[Message]) -> dict[str, BaseModel]:
        """Получает из бд персоны и сохраняет в сообщение.

        :param conn:
        :param messages:
        :rtype: dict[str, BaseModel]
        """
        sql = '''
            SELECT
                p.id,
                p.full_name
            FROM content.person p
            WHERE p.id = ANY($1)
        '''

        ids = [m.obj_id for m in messages]
        person_map = dict()
        async with conn.transaction():
            async for row in conn.cursor(sql, ids, prefetch=self.chunk_size):
                person_map[row['id']] = Person(**row)
        return person_map
