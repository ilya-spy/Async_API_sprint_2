import logging
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.film_cache import FilmCacheService
from services.film_elastic import FilmElasticService

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 50


class Offset:
    def __init__(self, offset: int, size: int):
        self.offset = offset
        self.size = size


def convert(page_id: Optional[int], page_size: Optional[int]) -> Offset:
    page = abs(page_id) if page_id else DEFAULT_PAGE
    page_size = abs(page_size) if page_size else DEFAULT_PAGE_SIZE
    offset = (page - 1 if page else 0) * page_size
    return Offset(offset, page_size)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self._cache = FilmCacheService(redis)
        self._elastic = FilmElasticService(elastic, index)
        self.index = index
        self._log = logging.getLogger("FilmService")

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """ Get Film by Id

        :param film_id:
        :return:
        :rtype: Optional[Film]
        """
        if film := await self._cache.get_one(film_id):
            self._log.debug("Film from cache")
            return film

        film = await self._elastic.get_one(film_id)
        if film:
            await self._cache.put_one(film)
        return film

    async def search(
            self,
            query: str,
            page: Optional[int],
            page_size: Optional[int]
    ) -> list[Film]:
        """ Search corresponding films

        @param query:
        @param page:
        @param page_size:
        @return: list[Film]
        """
        pg = convert(page, page_size)
        if films := await self._cache.get_search(query, pg.offset, pg.size):
            self._log.debug("Search results from cache")
            return films
        resp = await self._elastic.get_search(query, pg.offset, pg.size)
        films = [Film(**entry['_source']) for entry in resp]
        if films:
            await self._cache.put_search(query, pg.offset, films)
        return films

    async def get_films(
            self,
            page: Optional[int],
            page_size: Optional[int],
            fltr_genre: Optional[str],
            sort_type: Optional[str]
    ) -> list[Film]:
        """ Get films by parameters

        @param page:
        @param page_size:
        @param fltr_genre:
        @param sort_type:
        @return: list[Film]
        """
        pg = convert(page, page_size)
        if films := await self._cache.get_films(
                pg.offset,
                pg.size,
                fltr_genre,
                sort_type
        ):
            self._log.debug("Films from cache")
            return films
        resp = await self._elastic.get_films(
            pg.offset,
            pg.size,
            fltr_genre,
            sort_type
        )
        films = [Film(**entry['_source']) for entry in resp]
        if films:
            await self._cache.put_films(
                pg.offset,
                fltr_genre,
                sort_type,
                films
            )
        return films


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmService:
    return FilmService(redis, elastic, 'films')
