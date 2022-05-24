
import logging
 
from uuid import UUID
from dataclasses import dataclass, asdict
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from aioredis import Redis

from services._cache import CacheAPI

@dataclass
class SearchCursor:
    page: Optional[int]
    size: Optional[int]
    sort: Optional[int]

    def __post_init__(self):
        self.offset = (self.page - 1) * self.size if self.page > 0 else 0

    def __repr__(self):
        return repr(
        f'SearchCursor::page={self.page},size={self.size},sort={self.sort}')


@dataclass
class SearchFilter:
    field: str
    query: Optional[str]
    filter: Optional[str]

    def __repr__(self):
        return repr(
        f'SearchFilter::field={self.field},query={self.query},filter={self.filter}')


class SearchAPI:
    def __init__(self, index: str, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic
        self.logger = logging.getLogger(f"SearchAPI: {index}")
        self.fetched = 0
        self.index = index


    @staticmethod
    def get_sort_query(sort_by: Optional[str]) -> Optional[dict]:
        sort = None
        if sort_by:
            if sort_by[0] == '-':
                sort = [{sort_by[1:]: {"order": "desc"}, }, ]
            else:
                sort = [{sort_by: {"order": "asc"}, }, ]
        return sort


    async def search_index(self, query: Optional[object],
                            cursor: SearchCursor) -> list[Optional[object]]:
        try:
            resp = await self.elastic.search(index=self.index,
                body={
                    "query": query
                },
                from_=cursor.offset,
                size=cursor.size,
                sort=SearchAPI.get_sort_query(cursor.sort),
            )
            self.logger.info('search: index=%s, query=%s, offset=%d, size=%d' % 
                                (self.index, query, cursor.offset, cursor.size))
        except NotFoundError:
            self.logger.exception("The requested index was not found")
            return []
        try:
            self.logger.info("Total found %d documents" % (resp['hits']['total']['value']))
            self.fetched += len(resp['hits']['hits'])
            return resp['hits']['hits']
        except KeyError:
            self.logger.exception("The requested query yielded no result")
            return []


    async def list_index(self, cursor: SearchCursor) -> list[Optional[object]]:
        """ List all available documents from the index with simple match_all query"""
        return await self.search_index({'match_all': {}}, cursor)


    async def match_field(self, cursor: SearchCursor, match: SearchFilter):
        """ Look up the specified text to appear in a specified field in all index docs"""
        query = {
            "match": {
                match.field: {
                    "query": match.query
                }
            }
        }
        return await self.search_index(query, cursor)


    async def look_single(uuid: UUID) -> Optional[object]:
        pass


class SearchService:
    def __init__(self, index: str, model: object, 
                    redis: Redis, elastic: AsyncElasticsearch):
        self.index = index
        self.cacher = CacheAPI(redis)
        self.searcher = SearchAPI(index, elastic)
        self.logger = logging.getLogger(f"SearchService: {index}")
        self.model = model


    async def list_all(self, page: Optional[int], size: Optional[int],
                sort: Optional[str]) -> list[Optional[object]]:
        """
        @param page:
        @param size:
        @param sort:
        @return: list[Optional[object]]
        """
        cursor = SearchCursor(page, size, sort)

        # look in cache upfront
        if cached := await self.cacher.get_index(self.index, repr(cursor)):
            self.logger.info("%s index get from cache: %s" 
                % (self.index, repr(SearchCursor(page, size, sort))))
            return cached

        # search all from elastic and convert
        resp = await self.searcher.list_index(cursor)

        converted = [self.model(**entry['_source']) for entry in (resp if resp else [])]
        self.logger.info(f"Fetched and converted {len(converted)} {self.index} elastic docs")

        # put page to cache
        await self.cacher.put_index(self.index, cursor,
            map(lambda o: asdict(o), converted)
        )
        self.logger.info("%s index put as key: %s"
            % (self.index, repr(SearchCursor(page, size, sort))))

        return converted


    async def search_field(self, field: str,
                query: Optional[str], filter: Optional[str],
                page: Optional[int], size: Optional[int],
                sort: Optional[str]) -> list[Optional[object]]:
        """
        @param field: top-level field in a docs to search on
        @param query: text to search within a field
        @param page:
        @param size:
        @param sort:
        @return: list[Optional[object]]
        """
        cursor = SearchCursor(page, size, sort)
        match = SearchFilter(field, query, filter)

        # look in cache upfront
        if cached := await self.cacher.get_index(self.index,
                                repr('_'.join([repr(cursor), repr(match)]))):
            self.logger.info("%s index get from cache: %s" 
                % (self.index, repr('_'.join([cursor, match]))))
            return cached

        # search for field matches in elastic
        resp = await self.searcher.match_field(cursor, match)

        converted = [self.model(**entry['_source'])
                        for entry in (resp if resp else [])]
        self.logger.info(
            f"Fetched and converted {len(converted)} {self.index} elastic docs")

        # put page to cache
        if len(converted):
            await self.cacher.put_index(self.index,
                                repr('_'.join([repr(cursor), repr(match)])),
                                map(lambda o: asdict(o), converted))
            self.logger.info("%s index put as key: %s"
                % (self.index, repr(SearchCursor(page, size, sort))))

        return converted
