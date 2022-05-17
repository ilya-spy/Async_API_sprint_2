from functools import lru_cache
from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

SearchParam = dict[str, Union[str, int]]

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 50


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.redis = redis
        self.elastic = elastic
        self.index = index

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """ Возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе

        :param film_id:
        :return:
        :rtype: Optional[Film]
        """
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def search(
            self,
            query: str,
            page: Optional[int],
            page_size: Optional[int]
    ) -> list[Film]:
        page = page if page else DEFAULT_PAGE
        page_size = page_size if page_size else DEFAULT_PAGE_SIZE
        offset = page * page_size
        films = await self._search_from_cache(query, offset, page_size)
        if not films:
            films = await self._get_search_from_elastic(
                query,
                offset,
                page_size
            )
            if films:
                params = {
                    "query": query,
                    "offset": offset,
                }
                await self._put_search_to_cache(params, films)
        return films

    async def get_films(
            self,
            page: Optional[int],
            page_size: Optional[int],
            fltr: Optional[str],
            sort_type: Optional[str]
    ) -> list[Film]:
        page = page if page else DEFAULT_PAGE
        page_size = page_size if page_size else DEFAULT_PAGE_SIZE
        offset = page * page_size

        return await self._get_films_from_elastic(
            offset,
            page_size,
            fltr,
            sort_type
        )

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index=self.index, id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _get_search_from_elastic(
            self,
            query: str,
            offset: int = 0,
            max_size: int = 50,
            sort_by: Optional[str] = "-imdb_rating"
    ) -> list[Film]:
        # If we're going to show more than 10k, we should use 'search_after'
        sort = [{sort_by: {"order": "asc"}, }, ] if sort_by else None
        matching = {
            "multi_match": {
                "query": query,
                "fields": ['title', 'description'],
                "operator": "or",
            }
        }
        try:
            resp = await self.elastic.search(
                index="movies",
                body={
                    "query": matching
                },
                from_=offset,
                size=max_size,
                sort=sort,
            )
        except NotFoundError:
            return []
        return resp['hits']['hits']

    async def _get_films_from_elastic(
            self,
            offset: Optional[int],
            size: Optional[int],
            fltr: Optional[str],
            sort_by: Optional[str]
    ) -> list[Film]:
        # If we're going to show more than 10k, we should use 'search_after'
        sort = [{sort_by: {"order": "asc"}, }, ] if sort_by else None
        query = {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "term": {fltr}
                }
            }
        } if fltr else {'match_all': {}}
        try:
            resp = await self.elastic.search(
                index="movies",
                body={
                    "query": query
                },
                from_=offset,
                size=size,
                sort=sort,
            )
        except NotFoundError:
            return []
        return resp['hits']['hits']

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """
        Пытаемся получить данные о фильме из кеша, используя команду get
        https://redis.io/commands/get

        :param film_id:
        :return:
        :rtype: Optional[Film]
        """
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _search_from_cache(
            self,
            query: str,
            offset: int = 0,
            max_size: int = 50
    ) -> list[Film]:
        return []

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(),
                             ex=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_search_to_cache(
            self,
            params: SearchParam,
            films: list[Film]
    ) -> bool:
        """ Put the search parameters and results in cahce"""
        return False


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        index: str = 'films',
) -> FilmService:
    return FilmService(redis, elastic, index)
