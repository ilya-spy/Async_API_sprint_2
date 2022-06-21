from functools import lru_cache

from fastapi import Depends

from core.elastic import AsyncElasticsearch
from core.redis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base import DocumentService


# get_genre_service — это провайдер GenreService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> DocumentService:
    return DocumentService('genres', Genre, redis, elastic)
