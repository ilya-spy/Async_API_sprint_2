import pytest

from genre_check import genre_page_check, genre_cache_check
from cmn_check import Changer


@pytest.mark.asyncio
class TestGenreEp:
    _URI = "genres/"

    @pytest.mark.parametrize("p_size, p_number, result",
                             [(100, 1, 200),
                              (10, 10, 200),
                              (0, 1, 422),
                              (10, 0, 422),
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
            genre_page_check(genres, response.body, p_size, p_number)
            changer = Changer("genres", "name", "test", get_es_entry_updater)
            await genre_cache_check(genres, self._URI, req_params, request_factory, changer)

    async def test_pages_wo_parameters(self, fill_es_genre, request_factory, no_cache, get_es_entry_updater):
        genres, failed = fill_es_genre
        response = await request_factory(self._URI)
        assert response.status == 200
        genre_page_check(genres, response.body)
        chngr = Changer("genres", "name", "test", get_es_entry_updater)
        await genre_cache_check(genres, self._URI, None, request_factory, chngr)
