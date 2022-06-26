import uuid

import pytest

from testdata.schemes.v1.converter import GenreConverter
from testdata.schemes.v1.genre import Genre


@pytest.mark.asyncio
class TestGenreIdEp:
    GENRE_BY_ID = "genres/{}/"

    @staticmethod
    async def check_cache(genre: Genre, request_factory, get_es_entry_updater):
        # corrupt data in es
        await get_es_entry_updater("genres", str(genre.id), {"name": "test_cache"})

        # request again - expecting old correct data to be cached
        response = await request_factory(TestGenreIdEp.GENRE_BY_ID.format(genre.id))
        assert response.status == 200

        # without cache data couldn't be equal
        assert Genre(**response.body) == GenreConverter.convert(genre)

        # return valid data to es
        await get_es_entry_updater("genres", str(genre.id), {"name": genre.name})

    @pytest.mark.parametrize("id_pos", [1, -1])
    async def test_id(self, id_pos, fill_es_genre, request_factory, get_es_entry_updater, no_cache):
        genres, _failed = fill_es_genre
        response = await request_factory(self.GENRE_BY_ID.format(genres[id_pos].id))

        assert response.status == 200
        assert Genre(**response.body) == GenreConverter.convert(genres[id_pos])
        await self.check_cache(genres[id_pos], request_factory, get_es_entry_updater)

    async def test_non_existent_id(self, fill_es_genre, request_factory):
        genres, _ = fill_es_genre
        wrong_id = uuid.uuid4()
        while wrong_id in (g.id for g in genres):
            wrong_id = uuid.uuid4()
        response = await request_factory(self.GENRE_BY_ID.format(wrong_id))
        assert response.status == 404

    @pytest.mark.parametrize("uid, expected_status", [("genre", 422), (123456789, 422)])
    async def test_incorrect_id(self, request_factory, uid, expected_status):
        response = await request_factory(self.GENRE_BY_ID.format(uid))
        assert response.status == expected_status
