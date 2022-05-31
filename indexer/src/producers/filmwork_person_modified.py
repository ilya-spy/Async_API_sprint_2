from producers.base import BaseProducer


class FilmworkPersonModifiedProducer(BaseProducer):
    """Находит все фильмы, в которых приняли участие персоны, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql.

        :rtype: str
        """
        return '''
            SELECT pfw.film_work_id as id, p.modified 
            FROM content.person p 
            INNER JOIN content.person_film_work pfw ON pfw.person_id = p.id
            WHERE p.modified > $1 
            ORDER BY p.modified DESC
        '''
