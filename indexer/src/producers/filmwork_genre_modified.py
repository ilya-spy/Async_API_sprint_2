from producers.base import BaseProducer


class FilmworkGenreModifiedProducer(BaseProducer):
    """Находит все фильмы с жанром, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT gfw.film_work_id as id, g.modified
            FROM content.genre g
            INNER JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
            WHERE g.modified > $1
            ORDER BY g.modified DESC
        '''
