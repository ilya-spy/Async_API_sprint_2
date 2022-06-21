from functools import lru_cache

from fastapi import Depends

from core.elastic import AsyncElasticsearch
from core.redis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base import DocumentService


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> DocumentService:
    return DocumentService('films', Film, redis, elastic)
