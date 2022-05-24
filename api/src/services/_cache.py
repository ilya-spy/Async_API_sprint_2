
import logging
from typing import Optional
from pprint import pprint

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

class CacheAPI:
    def __init__(self, redis) -> None:
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI")

    async def get_single(self, key: str) -> Optional[object]:
        pass


    async def put_single(self, key: str, val: str) -> str:
        pass


    async def get_index(self, index: str, key: str) -> list[Optional[object]]:
        pass


    async def put_index(self, index: str, key: str, data: list[object]) -> int:
        pass

    async def drop_index(self, index, key: str) -> int:
        pass