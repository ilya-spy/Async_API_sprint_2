from http import HTTPStatus
import pytest

from checker import APIChecker
from tester import APITester
from converter import GenreConverter

from testdata.models.factory import Factory


@pytest.mark.asyncio
@pytest.mark.usefixtures("genres")
class TestGenreIdEp:
    INDEX = "genres"
    GENRE_BY_ID = "genres/{}/"
    GENRES_LIST = "genres/"
    GENRES_COUNT = 100

    async def test_non_existent_id(self, http_requester, genres: Factory):
        """Test makes sure API returns non-existent status accordingly"""

        await APITester.test_non_existent_id(self.GENRE_BY_ID, http_requester, genres)

    @pytest.mark.parametrize("uid, expected_status", [
        ("wrong_genre_id", HTTPStatus.UNPROCESSABLE_ENTITY), (123456789, HTTPStatus.UNPROCESSABLE_ENTITY)
    ])
    async def test_incorrect_id(self, http_requester, uid, expected_status):
        """Test makes sure API returns wrong arguments status on incorrct genre uuid entries"""

        await APITester.test_incorrect_id(self.GENRE_BY_ID, http_requester, uid, expected_status)

    @pytest.mark.parametrize("page", [1, 2])
    async def test_page(self, page, http_requester, get_es_updater, genres: Factory):
        """Test makes sure API correctly returns and orders existing elements and pages"""

        await APITester.test_page(self.GENRES_LIST, GenreConverter, page, http_requester, get_es_updater, genres)

    @pytest.mark.parametrize("p_size, p_number, result",
                             [(100, 1, HTTPStatus.OK),
                              (10, 10, HTTPStatus.OK),
                              (0, 1, HTTPStatus.UNPROCESSABLE_ENTITY),
                              (10, 0, HTTPStatus.UNPROCESSABLE_ENTITY),
                              (-50, 1, HTTPStatus.UNPROCESSABLE_ENTITY),
                              (50, -1, HTTPStatus.UNPROCESSABLE_ENTITY),
                              (500, 65535, HTTPStatus.NOT_FOUND)])
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
        if result == HTTPStatus.OK:
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
