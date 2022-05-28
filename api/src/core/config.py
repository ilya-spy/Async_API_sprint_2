import logging
import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
if os.environ.get('DEBUG'):
    logging.info('Enabling debug logging...')
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
APP_PORT = int(os.getenv('APP_PORT', 8000))
APP_LIVE_RELOAD = bool(os.getenv('APP_LIVE_RELOAD', True))

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_SCHEME = os.getenv('ELASTIC_SCHEME', 'http')
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Натсройка Postgres
PG_DSN = dict(
    database=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST', '127.0.0.1'),
    port=os.environ.get('DB_PORT', 5432),
    server_settings=dict(
        search_path='public,content',
    ),
)

# Настройка индексатора
ETL_STORAGE_STATE_KEY = os.getenv('ETL_STORAGE_STATE_KEY', 'indexer')
ETL_PRODUCER_CHUNK_SIZE = int(os.getenv('ETL_PRODUCER_CHUNK_SIZE', 500))
ETL_PRODUCER_QUEUE_SIZE = int(os.getenv('ETL_PRODUCER_QUEUE_SIZE', 500))
ETL_PRODUCER_CHECK_INTERVAL = int(os.getenv('ETL_PRODUCER_CHECK_INTERVAL', 10))
ETL_LOADER_CHUNK_SIZE = int(os.getenv('ETL_LOADER_CHUNK_SIZE', 100))
ETL_ENRICHER_MAX_BATCH_SIZE = int(os.getenv('ETL_ENRICHER_MAX_BATCH_SIZE', 100))
ETL_ENRICHER_CHUNK_SIZE = int(os.getenv('ETL_ENRICHER_CHUNK_SIZE', 100))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
