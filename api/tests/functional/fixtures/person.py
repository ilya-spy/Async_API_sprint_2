import pytest

from testdata.models.factory import Factory
from testdata.models.person import Person as PersonModel

from src.test_person import TestPersonIdEp


@pytest.fixture(scope='class')
async def persons(es_client, es_bulk, backend_cleaner) -> Factory:
    """Setup Genre-specific fixtures to use in TestGenreIdEp class"""

    # Reset backend
    await backend_cleaner(TestPersonIdEp.INDEX)

    # Produce genres
    factory = Factory(TestPersonIdEp.INDEX, PersonModel)
    factory.inflate(TestPersonIdEp.PERSON_COUNT)

    # Perform index actions
    success, failure = await es_bulk(
        es_client,
        actions=factory.actions()
    )
    await es_client.indices.refresh()

    print(factory.product[0])
    yield factory

    # Reset backend
    await backend_cleaner(TestPersonIdEp.INDEX)
