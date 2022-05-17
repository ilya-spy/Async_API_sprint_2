import logging
from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()

logger = logging.getLogger(__name__)


class Film(BaseModel):
    id: str
    title: str


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(id=film.id, title=film.title)


@router.get("/")
async def films_by_imdb(
        sort: Union[str, None],
        pg_size: Union[int, None] = Query(default=None, alias="page[size]"),
        pg_number: Union[int, None] = Query(
            default=None,
            alias="page[number]"
        ),
        fltr: Union[str, None] = Query(default=None, alias="filter[genre]")
) -> int:
    if fltr:
        await get_films(pg_size, pg_number, sort)
    else:
        await get_films(pg_size, pg_number, sort)
    return 0


async def get_films(chunk_size: int, chunk_number: int, sort_type: str):
    logger.debug(
        f"Films request: page: {chunk_number}, entries: {chunk_size},"
        f" sorted by {sort_type}"
    )
    return 0


async def get_filtred_films(
        fltr: str,
        chunk_size: int,
        chunk_number: int,
        sort_type: str
):
    logger.debug(
        f"Films request with filter: filter {fltr}, page: {chunk_number},"
        f" entries: {chunk_size}, sorted by {sort_type}"
    )
    return 1


@router.get("/search")
async def search_films(request: Request) -> int:
    print(request)
    return 0
