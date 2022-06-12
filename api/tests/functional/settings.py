import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_SCHEME: str = os.environ.get('API_SCHEME', 'http')
    API_HOST: str = os.environ.get('API_HOST', '127.0.0.1')
    API_PORT: int = os.environ.get('API_PORT', 8000)

    REDIS_HOST: str = os.environ.get('REDIS_HOST', '127.0.0.1')
    REDIS_PORT: int = os.environ.get('REDIS_PORT', 6379)

    ELASTIC_SCHEME: str = os.environ.get('ELASTIC_SCHEME', 'http')
    ELASTIC_HOST: str = os.environ.get('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT: int = os.environ.get('ELASTIC_PORT', 9200)

    SECRET_KEY: str = os.environ.get('SECRET_KEY', '')

    LOGGING_LEVEL: str = os.environ.get('LOGGING_LEVEL', 'INFO')


settings = Settings()
