from testdata.schemes.v1.genre import Genre
from testdata.models.genre import Genre as GenreModel


class GenreConverter:
    @staticmethod
    def convert(model: GenreModel) -> Genre:
        return Genre(
            uuid=model.id,
            name=model.name
        )
