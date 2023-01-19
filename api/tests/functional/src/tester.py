import uuid
from http import HTTPStatus

from checker import APIChecker
from testdata.models.factory import Factory


class APITester:

    @staticmethod
    async def test_non_existent_id(endpoint_by_id: str, http_requester, factory: Factory):
        """Test makes sure API returns non-existent status accordingly"""

        # Make sure no duplications
        wrong_id = uuid.uuid4()
        while wrong_id in [g['id'] for g in factory.production()]:
            wrong_id = uuid.uuid4()

        response = await http_requester(endpoint_by_id.format(wrong_id))
        assert response.status == HTTPStatus.NOT_FOUND

    @staticmethod
    async def test_incorrect_id(endpoint_by_id: str, http_requester, uid, expected_status):
        """Test makes sure API returns wrong arguments status on incorrct uuid entries"""

        response = await http_requester(endpoint_by_id.format(uid))
        assert response.status == expected_status

    @staticmethod
    async def test_page(endpoint_list, converter, page, http_requester, get_es_updater, factory: Factory):
        """Test makes sure API correctly returns and orders existing elements and pages"""

        checker = APIChecker(
            endpoint_list,
            converter,
            http_requester,
            get_es_updater,
            {"page[number]": page}
        )
        await checker.check_response_page(factory.production())
