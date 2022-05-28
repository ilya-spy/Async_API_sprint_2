import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

from models.film import Film

ELASTIC_INDEX = "films"
ELASTIC_SEARCH_FIELDS = ['title', 'description']


class FilmElasticService:
    def __init__(
            self,
            elastic: AsyncElasticsearch,
            index: str = ELASTIC_INDEX
    ):
        self._elastic = elastic
        self.logger = logging.getLogger("FilmElasticService")
        self.index = index

    async def get_one(self, film_id: str) -> Optional[Film]:
        """

        @param film_id:
        @return:
        """
        try:
            doc = await self._elastic.get(index=self.index, id=film_id)
        except NotFoundError:
            self.logger.exception("")
            return None
        film = doc.get('_source')
        return Film(**film) if film else None

    async def get_search(
            self,
            query: str,
            offset: int = 0,
            max_size: int = 50,
            sort_by: Optional[str] = None
    ) -> list[Film]:
        """

        @param query:
        @param offset:
        @param max_size:
        @param sort_by:
        @return:
        """
        # If we're going to show more than 10k, we should use 'search_after'
        matching = {
            "multi_match": {
                "query": query,
                "fields": ELASTIC_SEARCH_FIELDS,
                "operator": "or",
            }
        }
        try:
            resp = await self._elastic.search(
                index=self.index,
                body={
                    "query": matching
                },
                from_=offset,
                size=max_size,
                sort=self._get_sort_query(sort_by),
            )
        except NotFoundError:
            self.logger.exception("")
            return []
        try:
            return resp['hits']['hits']
        except KeyError:
            self.logger.exception("Answer doesn't contain films")
            return []

    async def get_films(
            self,
            offset: Optional[int],
            size: Optional[int],
            genre_id: Optional[str],
            sort_by: Optional[str]
    ) -> list[Film]:
        """

        @param offset:
        @param size:
        @param genre_id:
        @param sort_by:
        @return:
        """
        # If we're going to show more than 10k, we should use 'search_after'
        query = {
            "nested": {
                "path": "genre",
                "query": {
                    "match": {
                        "genre.id": {
                            "query": genre_id,
                        },
                    },
                },
            },
        } if genre_id else {'match_all': {}}

        try:
            resp = await self._elastic.search(
                index=self.index,
                body={
                    "query": query,
                },
                from_=offset,
                size=size,
                sort=self._get_sort_query(sort_by),
            )
        except NotFoundError:
            self.logger.exception("")
            return []
        try:
            return resp['hits']['hits']
        except KeyError:
            self.logger.exception("Answer doesn't contain films")
            return []

    @staticmethod
    def _get_sort_query(sort_by: Optional[str]) -> Optional[dict]:
        sort = None
        if sort_by:
            if sort_by[0] == '-':
                sort = [{sort_by[1:]: {"order": "desc"}, }, ]
            else:
                sort = [{sort_by: {"order": "asc"}, }, ]
        return sort
