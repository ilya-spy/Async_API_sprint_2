from pydantic import BaseModel
from typing import Callable, Generator

from converter import BaseConverter


class APIChecker:
    """Class with methods to check API responses for consistency"""

    DEFAULT_PAGE_SIZE = 50
    DEFAULT_PAGE_NUMBER = 1

    def __init__(self,
                 endpoint: str,
                 converter: BaseConverter,
                 requester: Callable,
                 updater: Callable,
                 params: dict) -> None:
        self.endpoint = endpoint
        self.converter = converter
        self.requester = requester
        self.updater = updater

        self.page_num = self.DEFAULT_PAGE_NUMBER
        if "page[number]" in params:
            self.page_num = params["page[number]"]
        self.page_size = self.DEFAULT_PAGE_SIZE
        if "page[size]" in params:
            self.page_size = params["page[size]"]

        self.params = {"page[number]": self.page_num, "page[size]": self.page_size}

    async def check_response(self, code) -> list[dict]:
        """Check request response code"""
        response = await self.requester(self.endpoint, self.params)

        assert response.status == code
        return response

    async def read_page(self) -> list[dict]:
        """Read request the page through API"""
        response = await self.requester(self.endpoint, self.params)

        assert response.status == 200
        return list(response.body)

    async def check_response_page(self, entries: Generator[BaseModel, None, None]):
        """Method checks provided API page response against db injected entries"""

        response = await self.read_page()
        entries = list(entries)

        # compute page boundaries inside index
        begin = (self.page_num - 1) * self.page_size
        end = begin + len(response) - 1
        middle = len(response) // 2

        # check page boundaries
        assert response[0] == self.converter.convert(entries[begin])
        assert response[-1] == self.converter.convert(entries[end])

        # check some middle element
        assert response[middle] == self.converter.convert(entries[begin + middle])

    async def check_cached_page(self, index: str, entries: Generator[BaseModel, None, None]):
        """Method checks provided API response to be cached (must differ from corrupted)"""

        # read API page to cache
        response = await self.read_page()
        entries = list(entries)

        # locate first element in page to alter
        begin = (self.page_num - 1) * self.page_size
        changed_uuid = self.converter.convert(entries[begin])['uuid']

        # corrupt internal id field (do not affect index id)
        await self.updater(index, changed_uuid, {'id': 'corrupted'})

        # expect to get from cache now
        response = await self.read_page()

        # without cache data couldn't be equal
        assert response[0] == self.converter.convert(entries[begin])

        # restore corrupted internal id
        await self.updater(index, changed_uuid, {'id': changed_uuid})
