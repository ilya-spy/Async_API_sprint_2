
import logging
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import Genre
from services._search import SearchAPI
from services._cache import CacheAPI


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.cacher = CacheAPI(redis)
        self.searcher = SearchAPI(elastic)
        self.logger = logging.getLogger("GenreService")

    async def list_genres(self, page, size, sort) -> list[Optional[Genre]]:
        """
        @param page:
        @param size:
        @param sort:
        @return: list[Optional[Genre]]
        """
        self.logger.info(f"page {page} type {type(page)}")
        self.logger.info(f"size {size} type {type(size)}")
        self.logger.info(f"sort {sort} type {type(sort)}")

        # look in cache upfront
        if genres := await self.cacher.get_index('genres', page, size, sort):
            self.logger.info("Genres list from cache")
            return genres

        # search all from elastic and convert
        resp = await self.searcher.list_index('movies', page, size, sort)
        converted = [Genre(**entry['_source']) for entry in resp]

        self.logger.info(f"Found and converted {len(converted)} genre docs")

        for genre in converted:
            # do not wait - put to cache
            self.cacher.put_single(str(genre.uuid), genre.name)
        return converted



# get_genre_service — это провайдер FilmService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
