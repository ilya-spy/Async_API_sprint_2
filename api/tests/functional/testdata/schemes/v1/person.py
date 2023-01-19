from testdata.models.model import BaseOrJsonModel


class PersonFilm(BaseOrJsonModel):
    film_uuid: str
    role: str
    title: str


class Person(BaseOrJsonModel):
    uuid: str
    full_name: str
    films: list[PersonFilm]
