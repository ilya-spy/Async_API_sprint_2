
from pydantic import BaseSettings


class Settings(BaseSettings):
    API_SCHEME: str = 'http'
    API_HOST: str = '127.0.0.1'
    API_PORT: int = 8001

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    ELASTIC_SCHEME: str = 'http'
    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    SECRET_KEY: str = ''

    LOGGING_LEVEL: str = 'INFO'
    DEBUG: str = 'True'


settings = Settings()
