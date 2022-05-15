from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import psycopg2
from psycopg2.extensions import connection, cursor


@dataclass
class DB:
    """Оберта для работы с бд."""
    dsn: dict
    _cursor_num: int = 0
    _conn: Optional[connection] = None

    def connected(self) -> bool:
        return self._conn and self._conn.closed == 0

    @contextmanager
    def cursor(self) -> cursor:
        """Возвращает курсор.
        Если кол-во открытых курсоров равно 0, закрывает соединение с бд."""
        try:
            if not self.connected():
                self._connect()
            self._cursor_num += 1
            yield self._conn.cursor()
        finally:
            self._cursor_num -= 1
            if self._cursor_num == 0:
                self._close()

    def _connect(self):
        self._close()
        self._conn = psycopg2.connect(**self.dsn)

    def _close(self):
        if self.connected():
            # noinspection PyBroadException
            try:
                self._conn.close()
            except Exception:
                pass

        self._conn = None
