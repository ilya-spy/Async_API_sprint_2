import uuid
import pytest

from testdata.schemes.v1.converter import GenreConverter
from testdata.schemes.v1.genre import Genre


@pytest.mark.asyncio
class TestGenreIdEp:
    uri = "genres/{}/"

    async def test_id(self, fill_es_genre, request_factory, get_cache_cleaner):
        genres, _failed = fill_es_genre
        ids = (0, int(len(genres) / 2), -1)
        await get_cache_cleaner()
        for pos in ids:
            response = await request_factory(self.uri.format(genres[pos].id))
            assert response.status == 200
            assert Genre(**response.body) == GenreConverter.convert(genres[pos])

    async def test_wrong_id(self, fill_es_genre, request_factory):
        genres, _ = fill_es_genre
        wrong_id = uuid.uuid4()
        while wrong_id in (g.id for g in genres):
            wrong_id = uuid.uuid4()
        response = await request_factory(self.uri.format(wrong_id))
        assert response.status == 404

    @pytest.mark.parametrize("in_data,expected", [("genre", 422), (123456789, 422)])
    async def test_wrong_id_type(self, request_factory, in_data, expected):
        response = await request_factory(self.uri.format(in_data))
        assert response.status == expected


_DEFAULT_PAGE_SIZE = 50
_DEFAULT_PAGE_NUMBER = 1


@pytest.mark.asyncio
class TestGenreEp:
    URI = "genres/"

    @staticmethod
    def _check_page(genres: list[Genre], resp_body: list[dict], p_size: int = _DEFAULT_PAGE_SIZE,
                    p_number: int = _DEFAULT_PAGE_NUMBER):
        page_size = g_len if (g_len := len(genres)) < p_size else p_size
        assert len(resp_body) == page_size
        pos = [0, int(page_size / 2), page_size - 1]
        for p in pos:
            assert Genre(**resp_body[p]) == GenreConverter.convert(genres[p])

    @pytest.mark.parametrize("page_size, page_number, result",
                             [(100, 1, 200), (-50, 1, 422), (50, -1, 422), (500, 65535, 404)])
    async def test_pages(self, page_size: int, page_number: int, result: int, fill_es_genre, request_factory,
                         get_cache_cleaner):
        await get_cache_cleaner()

        genres, failed = fill_es_genre
        params = {"page[size]": page_size, "page[number]": page_number}
        response = await request_factory(self.URI, params=params)
        assert response.status == result
        if response.status == 200:
            self._check_page(genres, response.body, page_size, page_number)

    async def test_pages_wo_parameters(self, fill_es_genre, request_factory):
        genres, failed = fill_es_genre
        response = await request_factory(self.URI, None)
        assert response.status == 200
        self._check_page(genres, response.body)
