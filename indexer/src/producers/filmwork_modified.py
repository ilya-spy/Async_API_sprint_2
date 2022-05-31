from producers.base import BaseProducer


class FilmworkModifiedProducer(BaseProducer):
    """Находит все фильмы, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT id, modified 
            FROM content.film_work
            WHERE modified > $1
            ORDER BY modified DESC
        '''
