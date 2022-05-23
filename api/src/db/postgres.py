from dataclasses import dataclass
from typing import Optional

import asyncpg
import orjson


@dataclass
class DB:
    """Оберта для работы с бд."""
    dsn: dict

    async def get_connection(self) -> asyncpg.connection.Connection:
        """ Создает соединение к бд.

        :rtype: asyncpg.connection.Connection
        """
        conn = await asyncpg.connect(**self.dsn)
        await conn.set_type_codec(
            'json',
            encoder=orjson.dumps,
            decoder=orjson.loads,
            schema='pg_catalog'
        )
        return conn


postgres: Optional[DB] = None


async def get_postgres() -> DB:
    return postgres
