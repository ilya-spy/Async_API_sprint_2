from typing import Optional

import pytest

from testdata.schemes.v1.converter import GenreConverter
from testdata.schemes.v1.genre import Genre

_DEFAULT_PAGE_SIZE = 50
_DEFAULT_PAGE_NUMBER = 1


@pytest.mark.asyncio
class TestGenreEp:
    GENRES_LIST = "genres/"

    @staticmethod
    async def _check_cache(genres: list[Genre], req_params: Optional[dict[str, int]], request_factory,
                           get_es_entry_updater):
        page_id = req_params["page[number]"] if "page[number]" in req_params else _DEFAULT_PAGE_NUMBER
        page_size = req_params["page[size]"] if "page[size]" in req_params else _DEFAULT_PAGE_SIZE
        check_begin = (page_id - 1) * page_size

        # corrupt data
        await get_es_entry_updater("genres", str(genres[check_begin].id), {"name": "test_cache"})

        # get from cache - need to set sort to match cached request
        response = await request_factory(TestGenreEp.GENRES_LIST, req_params)
        assert response.status == 200

        # without cache data couldn't be equal
        assert Genre(**response.body[0]) == GenreConverter.convert(genres[check_begin])

        # return correct data
        await get_es_entry_updater("genres", str(genres[check_begin].id), {"name": genres[check_begin].name})

    @staticmethod
    def _check_page(genres: list[Genre], resp_body: list[dict],
                    page_size: int = _DEFAULT_PAGE_SIZE, page_number: int = _DEFAULT_PAGE_NUMBER):
        assert len(resp_body) > 0

        # compute page boundaries inside index
        first_index = (page_number - 1) * page_size
        last_index = first_index + len(resp_body) - 1
        middle_index = len(resp_body) // 2

        # check page boundaries
        assert Genre(**resp_body[0]) == GenreConverter.convert(genres[first_index])
        assert Genre(**resp_body[-1]) == GenreConverter.convert(genres[last_index])

        # check some middle element
        assert Genre(**resp_body[middle_index]) == GenreConverter.convert(
            genres[first_index + middle_index]
        )

    @pytest.mark.parametrize("p_size, p_number, result",
                             [(100, 1, 200),
                              (10, 10, 200),
                              (-50, 1, 422),
                              (50, -1, 422),
                              (500, 65535, 404)])
    async def test_pages(self, p_size: int, p_number: int, result: int, fill_es_genre, request_factory, no_cache,
                         get_es_entry_updater):
        # populate and sort test genres
        genres, failed = fill_es_genre
        genres.sort(key=lambda x: x.id)

        # request specific page, sorted by uuid
        req_params = {"page[size]": p_size, "page[number]": p_number, "sort": "id"}
        response = await request_factory(self.GENRES_LIST, params=req_params)
        assert response.status == result

        if result == 200:
            self._check_page(genres, response.body, p_size, p_number)
            await self._check_cache(genres, req_params, request_factory, get_es_entry_updater)

    async def test_pages_wo_parameters(self, fill_es_genre, request_factory, no_cache, get_es_entry_updater):
        # populate and sort test genres
        genres, failed = fill_es_genre
        genres.sort(key=lambda x: x.id)

        # request default page
        req_params = {"sort": "id"}
        response = await request_factory(self.GENRES_LIST, params=req_params)
        assert response.status == 200

        self._check_page(genres, response.body)
        await self._check_cache(genres, req_params, request_factory, get_es_entry_updater)
