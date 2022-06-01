import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Класс содержит описание окружения и значения по умолчанию"""
    """Pydantic проверяет переменные окружения, приводит типы и заполняет умолчания"""

    # Включить дебаг режим в контейнерах приложения
    DEBUG: bool = False

    # Настройки Postgres
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 5432
    DB_SCHEMA: str = 'content'

    # Настройки Elasticsearch
    ELASTIC_SCHEME: str = 'http'
    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    # Настройки Redis
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    # Настройка индексатора
    ETL_STORAGE_STATE_KEY: str = 'indexer'
    ETL_PRODUCER_CHUNK_SIZE: int = 500
    ETL_PRODUCER_QUEUE_SIZE: int = 500
    ETL_PRODUCER_CHECK_INTERVAL: int = 10
    ETL_LOADER_CHUNK_SIZE: int = 100
    ETL_ENRICHER_MAX_BATCH_SIZE: int = 100
    ETL_ENRICHER_CHUNK_SIZE: int = 100

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
