
import logging
from typing import Optional


CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

class CacheAPI:
    def __init__(self, redis) -> None:
        self.redis = redis
        self.logger = logging.getLogger("CacheAPI")

    async def get_single(key: str) -> Optional[object]:
        pass


    async def put_single(key: str, val: str) -> str:
        pass


    async def get_index(index: str, offset: Optional[int], size: Optional[int],
                         sort: Optional[str]) -> list[Optional[object]]:
        pass


    async def put_index(index: str, tuples: list[tuple[str,str]]) -> list[str]:
        pass