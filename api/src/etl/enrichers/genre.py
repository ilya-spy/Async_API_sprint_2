from dataclasses import dataclass

from asyncpg.connection import Connection
from pydantic import BaseModel

from etl.entities import Genre, Message

from .base import BaseEnricher


@dataclass
class GenreEnricher(BaseEnricher):
    """Получает из бд полные данные по жанру."""

    async def retrieve_models(self, conn: Connection, messages: list[Message]) -> dict[str, BaseModel]:
        """Получает из бд жанры и сохраняет в сообщение.

        :param conn:
        :param messages:
        :rtype: dict[str, BaseModel]
        """
        sql = '''
            SELECT
                g.id,
                g.name
            FROM content.genre g
            WHERE g.id = ANY($1)
        '''

        ids = [m.obj_id for m in messages]
        genre_map = dict()
        async with conn.transaction():
            async for row in conn.cursor(sql, ids, prefetch=self.chunk_size):
                genre_map[row['id']] = Genre(**row)
        return genre_map
