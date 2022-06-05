from typing import Generator

from factory.fuzzy import FuzzyText
from faker import Faker
from testdata.models.genre import Genre


class GenreFactory:
    @staticmethod
    def create(count: int) -> list[Genre]:
        if count <= 0:
            return []
        out = []
        fk = Faker()
        Faker.seed(seed=4231)
        namer = FuzzyText(length=15)
        for i in range(count):
            out.append(Genre(id=fk.uuid4(), name=namer.fuzz()))
        return out

    @staticmethod
    def create_by_one(count: int) -> Generator[dict, None, None]:
        if count <= 0:
            return
        fk = Faker()
        fk.seed(seed=4231)
        namer = FuzzyText(length=15)
        for i in range(count):
            one = Genre(id=fk.uuid4(), name=namer.fuzz())
            yield {"_id": one.id, "_source": one.dict(), }

    @staticmethod
    def from_list_by_one(genres: list[Genre]) -> Generator[dict, None, None]:
        for one in genres:
            yield {"_id": one.id, "_source": one.dict(), }
