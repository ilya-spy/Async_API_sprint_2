from typing import Optional

from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    """Функция для DI клиента Elasticsearch

    :return: Возвращает клиента Elasticsearch
    :rtype: AsyncElasticsearch
    """
    return es
