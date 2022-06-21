import logging
from typing import Optional

from interfaces.search import SearchCursor, SearchRequest
from core.elastic import AsyncElasticsearch, ElasticSearcher
from core.redis import Redis, RedisCacher


class DocumentService:
    """API Service providing cache-enabled operations in an indexed document database"""
    def __init__(self, index: str, model: object,
                 redis: Redis, elastic: AsyncElasticsearch):
        self.index = index
        self.cacher = RedisCacher(index, redis)
        self.searcher = ElasticSearcher(index, elastic)
        self.logger = logging.getLogger(f"DocumentService: {index}")
        self.model = model

    async def list_all(self, page: Optional[int], size: Optional[int],
                       sort: Optional[str]) -> list[Optional[object]]:
        """List all documents in the index, with sorting by field"""
        cursor = SearchCursor(page, size, sort)

        # look in cache upfront
        if cached := await self.cacher.get_vector(repr(cursor)):
            self.logger.info("%s index get from cache: %s"
                             % (self.index, repr(cursor)))
            return [self.model(**c) for c in cached]

        # search all from elastic and convert
        resp = await self.searcher.list_index(cursor)

        converted = [self.model(**entry) 
                     for entry in (resp if resp else [])]
        self.logger.info(
            f"Fetched and converted {len(converted)} {self.index} elastic docs")

        # put page to cache
        await self.cacher.put_vector(repr(cursor), converted)
        return converted

    async def search_by_field(
            self,
            path: str,
            query: Optional[str],
            page: Optional[int],
            size: Optional[int],
            sort: Optional[str]
    ) -> list[Optional[object]]:
        """ Looking for docs where specific field matches query"""

        cursor = SearchCursor(page, size, sort)
        match = SearchRequest(path, query)
        key = ('_'.join([repr(cursor), repr(match)]))

        # look in cache upfront
        if cached := await self.cacher.get_vector(key):
            self.logger.info(
                f"{self.index} index get from cache: {key}")
            return [self.model(**c) for c in cached]

        # search for field matches in elastic
        resp = await self.searcher.search_index(cursor, match)
        converted = [self.model(**entry)
                     for entry in (resp if resp else [])]
        self.logger.info(
            f"Fetched and converted {len(converted)} {self.index} elastic docs"
        )

        # put page to cache
        if converted:
            await self.cacher.put_vector(
                key,
                list(map(lambda o: o.dict(), converted)))
            self.logger.info(
                f"{self.index} index put as key: {key}")
        return converted

    async def get_single(self, uuid: str) -> Optional[object]:
        """Get a single document, knowing its identifier directly"""

        # look in cache upfront
        if cached := await self.cacher.get_scalar(uuid):
            self.logger.info("%s id record get from cache: %s"
                             % (self.index, cached))
            return self.model(**cached)

        result = await self.searcher.get_document(uuid)
        self.logger.info("got result search: " + str(result))
        if result:
            response = self.model(**result)
            await self.cacher.put_scalar(uuid, response)
            self.logger.info("object cached as key: %s" % uuid)
            return response
        return None
