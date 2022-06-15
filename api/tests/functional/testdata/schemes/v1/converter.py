from testdata.models.genre import Genre as GenreModel
from testdata.schemes.v1.genre import Genre


class GenreConverter:
    @staticmethod
    def convert(model: GenreModel) -> Genre:
        return Genre(
            uuid=model.id,
            name=model.name
        )
