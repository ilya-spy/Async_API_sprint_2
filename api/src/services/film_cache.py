from typing import Optional, Union

from aioredis import Redis

from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

SearchParam = dict[str, Union[str, int]]


class FilmCacheService:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def get_one(self, film_id: str) -> Optional[Film]:
        """ Get film by id

        :param film_id:
        :return:
        :rtype: Optional[Film]
        """
        data = await self._redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def put_one(self, film: Film):
        """Store film

        @param film:
        """
        await self._redis.set(
            film.id,
            film.json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_search(
            self,
            query: str,
            offset: int = 0,
            max_size: int = 50
    ) -> list[Film]:
        """Get search result

        @param query:
        @param offset:
        @param max_size:
        @return:list[Film]
        """
        return []

    async def put_search(
            self,
            query: Optional[str],
            offset: int,
            films: list[Film]
    ):
        """Store the search parameters and results

        @param query:
        @param offset:
        @param films:
        """

    async def get_films(
            self,
            offset: Optional[int],
            size: Optional[int],
            fltr: Optional[str],
            sort_by: Optional[str]
    ) -> list[Film]:
        """Get films by parameters

        @param offset:
        @param size:
        @param fltr:
        @param sort_by:
        @return: list[Film]
        """
        return []

    async def put_films(
            self,
            offset: Optional[int],
            fltr: Optional[str],
            sort_by: Optional[str],
            films: list[Film]
    ):
        """Store the request parameters and results

        @param offset:
        @param fltr:
        @param sort_by:
        @param films:
        """
