import multiprocessing
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Класс содержит описание окружения и значения по умолчанию"""
    """Pydantic проверяет переменные окружения, приводит типы и заполняет умолчания"""

    # Включить дебаг режим в контейнерах приложения
    DEBUG: bool = False

    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = 'movies'

    # Настройки Unicorn/FastAPI
    APP_HOST: str = '127.0.0.1'
    APP_PORT: int = 8000
    APP_WORKERS: int =  multiprocessing.cpu_count() * 2 + 1
    APP_WORKERS_CLASS: str = 'uvicorn.workers.UvicornWorker'

    # Настройки Redis
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    # Настройки Elasticsearch
    ELASTIC_SCHEME: str = 'http'
    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
