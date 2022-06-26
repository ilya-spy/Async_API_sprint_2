from typing import Optional

from cmn_check import Changer, SchemeType, page_check, cache_check, DEFAULT_PAGE_SIZE, DEFAULT_PAGE_NUMBER
from testdata.schemes.v1.genre import Genre
from testdata.schemes.v1.converter import GenreConverter


def get_changer(get_es_entry_updater) -> Changer:
    return Changer("genres", "name", get_es_entry_updater)


def genre_page_check(entries: list[SchemeType], resp_body: list[dict], p_size: int = DEFAULT_PAGE_SIZE,
                     p_number: int = DEFAULT_PAGE_NUMBER):
    page_check(Genre, GenreConverter.convert, entries, resp_body, p_size, p_number)


async def genre_cache_check(entries: list[SchemeType], uri: str, req_params: Optional[dict[str, int]],
                            request_factory, changer: Changer):
    await cache_check(Genre, GenreConverter.convert, entries, uri, req_params, request_factory, changer)
