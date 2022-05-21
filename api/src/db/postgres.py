from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Optional

import asyncpg


@dataclass
class DB:
    """Оберта для работы с бд."""
    dsn: dict

    async def get_connection(self) -> asyncpg.connection.Connection:
        """ Создает соединение к бд.

        :rtype: asyncpg.connection.Connection
        """
        conn = await asyncpg.connect(**self.dsn)
        return conn

    @contextmanager
    async def cursor(self, *args, **kwargs) -> Generator[asyncpg.Record, None, None]:
        """Выполняет асинхронный запрос в бд и возвращает ответ.
        Если кол-во открытых курсоров равно 0, закрывает соединение с бд.

        :param args:
        :param kwargs:
        :return:
        """
        conn = await asyncpg.connect(**self.dsn)
        try:
            async with conn.transaction():
                async for row in conn.cursor(*args, **kwargs):
                    yield row
        finally:
            await conn.close()


postgres: Optional[DB] = None


async def get_postgres() -> DB:
    return postgres
