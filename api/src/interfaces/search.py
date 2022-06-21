from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


# Search interfaces


@dataclass
class SearchCursor:
    """Interface to provide cursor parameters for a search reqeust"""
    page: Optional[int]
    size: Optional[int]
    sort: Optional[int]

    def __post_init__(self):
        self.offset = (self.page - 1) * self.size if self.page > 0 else 0

    def __repr__(self):
        return f'SearchCursor::page={self.page},size={self.size},sort={self.sort}'


@dataclass
class SearchRequest:
    """Interface to provide matching parameters when searching documents in index"""
    path: str
    query: Optional[str]

    def __repr__(self):
        return f'SearchFilter::field={self.path},query={self.query}'


class SearchAPI(ABC):
    """Interface class to support common search tasks for indexed data"""

    @abstractmethod
    async def list_index(self, cursor: SearchCursor) -> list[object]:
        """List all documents in an index, starting at cursor"""
        pass

    @abstractmethod
    async def search_index(self, cursor: SearchCursor, request: SearchRequest) -> list[object]:
        """Search documents in an index, using cursor and filter to query on a field"""
        pass

    @abstractmethod
    async def get_document(self, uuid: UUID) -> Optional[object]:
        """Retrieve specific document from database, using its identifier"""
        pass
