from dataclasses import dataclass
from typing import Optional


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
