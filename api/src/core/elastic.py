import logging
from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError

from interfaces.search import SearchAPI, SearchCursor, SearchRequest


class ElasticSearcher(SearchAPI):
    def __init__(self, index: str, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic
        self.logger = logging.getLogger(f"ElasticSearcher: {index}")
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

    async def query_elastic(self,
                            query: Optional[object],
                            cursor: SearchCursor) -> list[Optional[object]]:
        try:
            sort_query = self.get_sort_query(cursor.sort)
            resp = await self.elastic.search(
                index=self.index,
                body={"query": query},
                from_=cursor.offset,
                size=cursor.size,
                sort=sort_query)

            self.logger.info('elastic: index=%s, query=%s, offset=%d, size=%d sort=%s' %
                             (self.index, query, cursor.offset, cursor.size, str(sort_query)))
        except NotFoundError:
            self.logger.exception("The requested index was not found")
            return []
        except Exception:
            self.logger.exception("The search request could not be performed as requested")
            return []

        try:
            self.logger.info(
                "Total found %d documents" % (resp['hits']['total']['value']))
            self.fetched += len(resp['hits']['hits'])
            return resp['hits']['hits']
        except KeyError:
            self.logger.exception("The requested query yielded no result")
            return []

    async def list_index(self, cursor: SearchCursor) -> list[object]:
        """ List all available documents from index with simple match_all query"""
        return await self.query_elastic({'match_all': {}}, cursor)

    async def search_index(self, cursor: SearchCursor, request: SearchRequest) -> list[object]:
        """Search documents in an index, using cursor and filter to query on a field"""
        parent = request.path.split('.')[0] if '.' in request.path else None
        target_query = {
            "match": {
                request.path: {
                    "query": request.query
                }
            }
        }
        parent_query = {
            "nested": {
                "path": parent,
                "query": target_query,
            },
        }
        return await self.query_elastic(
            parent_query if parent else target_query,
            cursor
        )

    async def get_document(self, uuid: UUID) -> Optional[object]:
        """Retrieve specific document from index, using its identifier"""
        try:
            doc = await self.elastic.get(index=self.index, id=uuid)
        except NotFoundError:
            return None
        return doc['_source']
