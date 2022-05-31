from producers.base import BaseProducer


class GenreModifiedProducer(BaseProducer):
    """Находит все жанры, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT g.id as id, g.modified
            FROM content.genre g 
            WHERE g.modified > $1
            ORDER BY g.modified DESC
        '''
