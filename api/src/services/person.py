from functools import lru_cache

from fastapi import Depends

from core.elastic import AsyncElasticsearch
from core.redis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import DocumentService


# get_genre_service — это провайдер DocumentService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтон)
@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> DocumentService:
    return DocumentService('persons', Person, redis, elastic)
