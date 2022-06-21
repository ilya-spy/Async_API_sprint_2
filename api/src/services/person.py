from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from core.elastic import AsyncElasticsearch, SearchService
from core.redis import Redis


# get_genre_service — это провайдер SearchService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтон)
@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SearchService:
    return SearchService('persons', Person, redis, elastic)
