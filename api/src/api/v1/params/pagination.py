from typing import Union

from fastapi import Query


class PaginationParams:
    def __init__(self,
                 page_size: Union[int, None] = Query(default=50, gt=0, alias='page[size]'),
                 page_number: Union[int, None] = Query(default=1, gt=0, alias='page[number]'),):
        self.page_size = page_size
        self.page_number = page_number
