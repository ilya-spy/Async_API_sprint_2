from typing import Optional

import pytest

from testdata.schemes.v1.converter import GenreConverter
from testdata.schemes.v1.genre import Genre

_DEFAULT_PAGE_SIZE = 50
_DEFAULT_PAGE_NUMBER = 1


@pytest.mark.asyncio
class TestGenreEp:
    _URI = "genres/"

    @staticmethod
    async def _check_cache(genres: list[Genre], req_params: Optional[dict[str, int]], request_factory,
                           get_es_entry_updater):
        page_id = _DEFAULT_PAGE_NUMBER
        page_size = _DEFAULT_PAGE_SIZE
        if req_params:
            page_id = req_params["page[number]"]
            page_size = req_params["page[size]"]
        check_begin = (page_id - 1) * page_size

        await get_es_entry_updater("genres", str(genres[check_begin].id), {"name": "test_cache"})
        # get from cache
        response = await request_factory(TestGenreEp._URI, req_params)
        assert response.status == 200

        # without catch data couldn't be equal
        assert Genre(**response.body[0]) == GenreConverter.convert(genres[check_begin])
        await get_es_entry_updater("genres", str(genres[check_begin].id), {"name": genres[check_begin].name})

    @staticmethod
    def _check_page(genres: list[Genre], resp_body: list[dict], p_size: int = _DEFAULT_PAGE_SIZE,
                    p_number: int = _DEFAULT_PAGE_NUMBER):
        assert len(resp_body) > 0
        check_begin = (p_number - 1) * p_size
        check_end = check_begin + len(resp_body) - 1
        positions = [
            (0, check_begin),
            (-1, check_end),
        ]
        for p in positions:
            resp_pos = p[0]
            check_pos = p[1]
            assert Genre(**resp_body[resp_pos]) == GenreConverter.convert(genres[check_pos])

    @pytest.mark.parametrize("p_size, p_number, result",
                             [(100, 1, 200),
                              (10, 10, 200),
                              (-50, 1, 422),
                              (50, -1, 422),
                              (500, 65535, 404)])
    async def test_pages(self, p_size: int, p_number: int, result: int, fill_es_genre, request_factory, no_cache,
                         get_es_entry_updater):
        genres, failed = fill_es_genre
        req_params = {"page[size]": p_size, "page[number]": p_number}
        response = await request_factory(self._URI, params=req_params)
        assert response.status == result
        if result == 200:
            self._check_page(genres, response.body, p_size, p_number)
            await self._check_cache(genres, req_params, request_factory, get_es_entry_updater)

    async def test_pages_wo_parameters(self, fill_es_genre, request_factory, no_cache, get_es_entry_updater):
        genres, failed = fill_es_genre
        response = await request_factory(self._URI)
        assert response.status == 200
        self._check_page(genres, response.body)
        await self._check_cache(genres, None, request_factory, get_es_entry_updater)
