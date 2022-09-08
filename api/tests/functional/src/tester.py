import uuid

import pytest

from checker import APIChecker
from converter import GenreConverter

from testdata.models.factory import Factory
from testdata.models.genre import Genre as GenreModel


@pytest.fixture(scope='class')
async def genres(es_client, es_bulk, backend_cleaner) -> Factory:
    """Setup Genre-specific fixtures to use in TestGenreIdEp class"""

    # Reset backend
    await backend_cleaner(TestGenreIdEp.INDEX)

    # Produce genres
    factory = Factory(TestGenreIdEp.INDEX, GenreModel)
    factory.produce(TestGenreIdEp.GENRES_COUNT)

    # Perform index actions
    success, failure = await es_bulk(
        es_client,
        actions=factory.actions()
    )
    await es_client.indices.refresh()

    yield factory

    # Reset backend
    await backend_cleaner(TestGenreIdEp.INDEX)


@pytest.mark.asyncio
@pytest.mark.usefixtures("genres")
class TestGenreIdEp:
    INDEX = "genres"
    GENRE_BY_ID = "genres/{}/"
    GENRES_LIST = "genres/"
    GENRES_COUNT = 100

    async def test_non_existent_id(self, http_requester, genres: Factory):
        """Test makes sure API returns non-existent status accordingly"""

        # Make sure no duplications
        wrong_id = uuid.uuid4()
        while wrong_id in [g['id'] for g in genres.production()]:
            wrong_id = uuid.uuid4()

        response = await http_requester(self.GENRE_BY_ID.format(wrong_id))
        assert response.status == 404

    @pytest.mark.parametrize("uid, expected_status", [("genre", 422), (123456789, 422)])
    async def test_incorrect_id(self, http_requester, uid, expected_status):
        """Test makes sure API returns wrong arguments status on incorrct genre uuid entries"""

        response = await http_requester(self.GENRE_BY_ID.format(uid))
        assert response.status == expected_status

    @pytest.mark.parametrize("page", [1, 2])
    async def test_page(self, page, http_requester, get_es_updater, genres: Factory):
        """Test makes sure API correctly returns and orders existing elements and pages"""

        checker = APIChecker(
            self.GENRES_LIST,
            GenreConverter,
            http_requester,
            get_es_updater,
            {"page[number]": page}
        )
        await checker.check_response_page(genres.production())

    @pytest.mark.parametrize("p_size, p_number, result",
                             [(100, 1, 200),
                              (10, 10, 200),
                              (0, 1, 422),
                              (10, 0, 422),
                              (-50, 1, 422),
                              (50, -1, 422),
                              (500, 65535, 404)])
    async def test_list_pages(self,
                              p_size,
                              p_number,
                              result,
                              http_requester,
                              get_es_updater,
                              genres: Factory
                              ):
        """Test checks cached paginated lists in API results"""
        req_params = {"page[size]": p_size, "page[number]": p_number}
        checker = APIChecker(
            self.GENRES_LIST,
            GenreConverter,
            http_requester,
            get_es_updater,
            req_params
        )
        await checker.check_response(result)
        if result == 200:
            await checker.check_cached_page(self.INDEX, genres.production())

    async def test_default_page(self, http_requester, get_es_updater, genres: Factory):
        """Test checks default page response"""

        # Create checker with empty params to test default
        checker = APIChecker(
            self.GENRES_LIST,
            GenreConverter,
            http_requester,
            get_es_updater,
            {}
        )

        # Read page from ES to fill in cache
        await checker.check_response_page(genres.production())

        # Read again to check that page was cached
        await checker.check_cached_page(self.INDEX, genres.production())
