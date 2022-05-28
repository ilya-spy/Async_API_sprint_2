import logging
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from services._cache import CacheAPI


@dataclass
class SearchCursor:
    page: Optional[int]
    size: Optional[int]
    sort: Optional[int]

    def __post_init__(self):
        self.offset = (self.page - 1) * self.size if self.page > 0 else 0

    def __repr__(self):
        return f'SearchCursor::page={self.page},size={self.size},sort={self.sort}'


@dataclass
class SearchFilter:
    field: str
    query: Optional[str]
    filter: Optional[str]

    def __repr__(self):
        return f'SearchFilter::field={self.field},query={self.query},filter={self.filter}'


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
            resp = await self.elastic.search(
                index=self.index,
                body={"query": query},
                from_=cursor.offset,
                size=cursor.size,
                sort=SearchAPI.get_sort_query(cursor.sort))
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
        # query = {
        #     "match": {
        #         match.field: {
        #             "query": match.query
        #         }
        #     }
        # }
        query = {
            "query_string": {
                "query": match.query,
                "default_field": "*"
            }
        }
        return await self.search_index(query, cursor)

    async def look_single(self, uuid: UUID, model: object) -> Optional[object]:
        try:
            doc = await self.elastic.get(index=self.index, id=uuid)
        except NotFoundError:
            return None
        return model(**doc['_source'])


class SearchService:
    def __init__(self, index: str, model: object,
                 redis: Redis, elastic: AsyncElasticsearch):
        self.index = index
        self.cacher = CacheAPI(index, redis)
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
                             % (self.index, repr(cursor)))
            return cached

        # search all from elastic and convert
        resp = await self.searcher.list_index(cursor)

        converted = [self.model(**entry['_source']) for entry in (resp if resp else [])]
        self.logger.info(f"Fetched and converted {len(converted)} {self.index} elastic docs")

        # put page to cache
        await self.cacher.put_index(self.index, repr(cursor), converted)
        self.logger.info("%s index put as key: %s"
                         % (self.index, repr(cursor)))

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
        if cached := await self.cacher.get_index(
                self.index,
                repr('_'.join([repr(cursor), repr(match)]))
        ):
            self.logger.info(
                "%s index get from cache: %s"
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
            await self.cacher.put_index(
                self.index,
                repr('_'.join([repr(cursor), repr(match)])),
                list(map(lambda o: o.json(), converted)))
            self.logger.info("%s index put as key: %s"
                             % (self.index, repr(SearchCursor(page, size, sort))))

        return converted

    async def get_single(self, uuid: UUID, model: object):
        # look in cache upfront
        if cached := await self.cacher.get_single(uuid):
            self.logger.info("%s id record get from cache: %s"
                             % (self.index, cached))
            return model(**cached)

        result = await self.searcher.look_single(uuid, model)
        self.logger.info("got result search: " + str(result))
        if result:
            await self.cacher.put_single(uuid, result)
            self.logger.info("object cached as key: %s" % uuid)
        return result
