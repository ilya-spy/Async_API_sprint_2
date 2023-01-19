from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from interfaces.search import SearchAPI
from interfaces.cache import CacheAPI
from models.film import Film
from services.base import DocumentService


@lru_cache()
def get_film_service(
        redis: CacheAPI = Depends(get_redis),
        elastic: SearchAPI = Depends(get_elastic)
) -> DocumentService:
    return DocumentService('films', Film, redis, elastic)
