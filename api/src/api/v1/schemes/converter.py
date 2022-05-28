from models.film import Film as FilmModel
from models.genre import Genre as GenreModel
from models.person import Person as PersonModel
from api.v1.schemes.film import Film, FilmBase
from api.v1.schemes.genre import Genre
from api.v1.schemes.person import PersonBase


class FilmBaseConverter:
    @staticmethod
    def convert(model: FilmModel) -> FilmBase:
        return FilmBase(
            uuid=model.id,
            title=model.title,
            imdb_rating=model.imdb_rating
        )


class FilmConverter:
    @staticmethod
    def convert(model: FilmModel) -> Film:
        def pers_base(persons: list[PersonModel]) -> list[PersonBase]:
            return [PersonBaseConverter.convert(prsn) for prsn in persons]

        return Film(
            uuid=model.id,
            title=model.title,
            imdb_rating=model.imdb_rating,
            description=model.description,
            genre=[GenreConverter.convert(gnr) for gnr in model.genre],
            actors=pers_base(model.actors),
            writers=pers_base(model.writers),
            directors=pers_base(model.directors),
        )


class GenreConverter:
    @staticmethod
    def convert(model: GenreModel) -> Genre:
        return Genre(
            uuid=model.id,
            name=model.name
        )


class PersonBaseConverter:
    @staticmethod
    def convert(model: PersonModel) -> PersonBase:
        return PersonBase(
            uuid=model.id,
            full_name=model.full_name
        )
