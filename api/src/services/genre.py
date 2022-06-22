from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from interfaces.search import SearchAPI
from interfaces.cache import CacheAPI
from models.genre import Genre
from services.base import DocumentService


# get_genre_service — это провайдер GenreService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_genre_service(
        redis: CacheAPI = Depends(get_redis),
        elastic: SearchAPI = Depends(get_elastic),
) -> DocumentService:
    return DocumentService('genres', Genre, redis, elastic)
