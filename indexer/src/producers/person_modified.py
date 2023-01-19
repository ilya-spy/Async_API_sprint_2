from producers.base import BaseProducer


class PersonModifiedProducer(BaseProducer):
    """Находит всех персон, чьи данные изменились с последнего синка."""

    def sql(self) -> str:
        """Возвращает sql-запрос.

        :rtype: str
        """
        return '''
            SELECT p.id as id, p.modified
            FROM content.person p
            WHERE p.modified > $1
            ORDER BY p.modified DESC
        '''
