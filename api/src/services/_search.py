
import logging
from typing import Optional

from elasticsearch import NotFoundError

from models.genre import Genre, UUID



class SearchAPI:
    def __init__(self, elastic) -> None:
        self.elastic = elastic
        self.logger = logging.getLogger("SearchAPI")
        self.fetched = 0


    @staticmethod
    def get_sort_query(sort_by: Optional[str]) -> Optional[dict]:
        sort = None
        if sort_by:
            if sort_by[0] == '-':
                sort = [{sort_by[1:]: {"order": "desc"}, }, ]
            else:
                sort = [{sort_by: {"order": "asc"}, }, ]
        return sort


    async def search_index(self, index: str, query: Optional[str], offset: Optional[int], 
                         size: Optional[int], sort: Optional[str]) -> list[Optional[object]]:
        try:
            resp = await self.elastic.search(index=index,
                body={
                    "query": query
                },
                from_=offset,
                size=size,
                sort=SearchAPI.get_sort_query(sort),
            )
        except NotFoundError:
            self.logger.exception("The requested index was not found")
            return []
        try:
            self.logger.info("Total fetched %d documents" % (resp['hits']['total']['value']))
            self.fetched += resp['hits']['total']['value']
            return resp['hits']['hits']
        except KeyError:
            self.logger.exception("The requested query yielded no result")
            return []


    async def list_index(self, index: str) -> list[Optional[object]]:
        self.search_index(index, {'match_all': {}})


    async def look_single(uuid: UUID) -> Optional[Genre]:
        pass
