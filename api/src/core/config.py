import logging
import os
from logging import config as logging_config

from core.logger import LOGGING

DEBUG = bool(os.environ.get('DEBUG', False))

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
if DEBUG:
    logging.info('Enabling debug logging...')
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
APP_PORT = int(os.getenv('APP_PORT', 8000))

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_SCHEME = os.getenv('ELASTIC_SCHEME', 'http')
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
