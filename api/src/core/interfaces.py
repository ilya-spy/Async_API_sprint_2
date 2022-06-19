from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


# Cache interfaces


class CacheIndex(BaseModel):
    """Class holding data values for vector-based cache keys"""
    values: list[dict]


class CacheAPI(ABC):
    """Interface class to support caching of scalar and vector keys"""

    @abstractmethod
    async def get_scalar(self, key: str) -> Optional[BaseModel]:
        """Get single scalar value from cache, using its key"""
        pass

    @abstractmethod
    async def put_scalar(self, key: str, obj: BaseModel) -> int:
        """Add a scalar value to cache, using key to index"""
        pass

    @abstractmethod
    async def get_vector(self, key: str) -> list[Optional[dict]]:
        """Fetches previously stored vector-based key"""
        pass

    @abstractmethod
    async def put_vector(self, key: str, data: list[dict]) -> int:
        """Adds a vector-based key to cache, allowing to store list data"""
        pass

    @abstractmethod
    async def drop_key(self, key: str) -> int:
        """Drop index from cache (delete all inner key-value pairs from it)"""
        pass


# Search interfaces


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


@dataclass
class SearchNestedField:
    field: str
    value: str

    def __repr__(self):
        return f'SearchNestedField::field={self.field},value={self.value}'
