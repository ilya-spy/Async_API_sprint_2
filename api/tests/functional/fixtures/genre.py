import pytest

from testdata.models.factory import Factory
from testdata.models.genre import Genre as GenreModel

from src.test_genre import TestGenreIdEp


@pytest.fixture(scope='class')
async def genres(es_client, es_bulk, backend_cleaner) -> Factory:
    """Setup Genre-specific fixtures to use in TestGenreIdEp class"""

    # Reset backend
    await backend_cleaner(TestGenreIdEp.INDEX)

    # Produce genres
    factory = Factory(TestGenreIdEp.INDEX, GenreModel)
    factory.inflate(TestGenreIdEp.GENRES_COUNT)

    # Perform index actions
    success, failure = await es_bulk(
        es_client,
        actions=factory.actions()
    )
    await es_client.indices.refresh()

    yield factory

    # Reset backend
    await backend_cleaner(TestGenreIdEp.INDEX)
