import logging
import os

from psycopg2.extras import DictCursor, register_uuid

register_uuid()

# Частота проверки обновлений
CHECK_INTERVAL_SEC = os.environ.get('CHECK_INTERVAL_SEC', 10)

# Кол-во загружаемых записей за раз из бд
CHUNK_SIZE = 1000

PG_DSN = dict(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST', '127.0.0.1'),
    port=os.environ.get('DB_PORT', 5432),
    options='-c search_path=public,content',
    cursor_factory=DictCursor,
)

REDIS_DSN = dict(
    host=os.environ.get('REDIS_HOST', '127.0.0.1'),
    port=os.environ.get('REDIS_PORT', 6379),
    db=os.environ.get('REDIS_DB', 0)
)

# ключ, по которому будет храниться состояние в хранилище
STORAGE_STATE_KEY = 'etl'

ES_SCHEMA = os.environ.get('ES_SCHEMA', 'https')
ES_HOST = os.environ.get('ES_HOST', '127.0.0.1')
ES_PORT = int(os.environ.get('ES_PORT', 9200))
ES_MAX_RETRIES = int(os.environ.get('ES_MAX_RETRIES', 3))
ES_MOVIE_INDEX_NAME = 'movies'
ES_SCHEMAS_PATH = '../elastic/schemas/*.json'

LOGGING_LEVEL = logging.DEBUG
