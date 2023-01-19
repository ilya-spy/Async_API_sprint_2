from http import HTTPStatus
import pytest

from tester import APITester
from converter import PersonConverter

from testdata.models.factory import Factory


@pytest.mark.asyncio
@pytest.mark.usefixtures("persons")
class TestPersonIdEp:
    INDEX = "persons"
    PERSON_BY_ID = "persons/{}/"
    PERSON_LIST = "persons/"
    PERSON_COUNT = 100

    async def test_non_existent_id(self, http_requester, persons: Factory):
        """Test makes sure API returns non-existent status accordingly"""

        await APITester.test_non_existent_id(self.PERSON_BY_ID, http_requester, persons)

    @pytest.mark.parametrize("uid, expected_status", [
        ("wrong_person_id", HTTPStatus.UNPROCESSABLE_ENTITY), (123456789, HTTPStatus.UNPROCESSABLE_ENTITY)
    ])
    async def test_incorrect_id(self, http_requester, uid, expected_status):
        """Test makes sure API returns wrong arguments status on incorrct person uuid entries"""

        await APITester.test_incorrect_id(self.PERSON_BY_ID, http_requester, uid, expected_status)

    @pytest.mark.parametrize("page", [1, 2])
    async def test_page(self, page, http_requester, get_es_updater, persons: Factory):
        """Test makes sure API correctly returns and orders existing elements and pages"""

        await APITester.test_page(self.PERSON_LIST, PersonConverter, page, http_requester, get_es_updater, persons)
