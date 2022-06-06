import pytest

from testdata.schemes.v1.converter import GenreConverter
from testdata.schemes.v1.genre import Genre


@pytest.mark.asyncio
class TestGenre:
    async def test_id(self, fill_es_genre, make_get_request):
        genres, failed = fill_es_genre
        middle_id = int(len(genres) / 2)
        response = await make_get_request("genres/{}/".format(genres[middle_id].id))

        assert response.status == 200
        assert Genre(**response.body) == GenreConverter.convert(genres[middle_id])

    async def test_search(self, fill_es_genre, make_get_request):
        genres, failed = fill_es_genre
        middle_id = int(len(genres) / 2)
        response = await make_get_request('genres/search', {'query': genres[middle_id].name})

        assert response.status == 200
        assert len(response.body) >= 1
