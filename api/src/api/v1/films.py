import logging
from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.schemes.converter import FilmBaseConverter, FilmConverter
from api.v1.schemes.film import Film, FilmBase
from services._search import SearchService
from services.film import get_film_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/search")
async def search_films(
        query: str,
        pg_size: int = Query(default=50, alias="page[size]"),
        pg_number: int = Query(default=1, alias="page[number]"),
        _film_service: SearchService = Depends(get_film_service)
) -> list[FilmBase]:
    """Search for 'query' in films

    @param query: - searching string
    @param pg_size: - max elements output
    @param pg_number: - offset
    @param _film_service: - internal parameter for work with storages
    @return list[FilmBase]: - corresponding films
    """
    # FixMe use such fields 'search_fields = ['title', 'description']'
    result = await _film_service.search_field(
        field='title',
        query=query,
        filter=None,
        page=pg_number,
        size=pg_size,
        sort=None
    )

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )
    return [FilmBaseConverter.convert(flm) for flm in result]


@router.get('/{film_id}/', response_model=Film)
async def film_details(
        film_id: UUID,
        film_service: SearchService = Depends(get_film_service)
) -> Film:
    """

    @param film_id: film unique identifier
    @param film_service: film extractor
    @return FilmDetails:
    """
    film = await film_service.get_single(str(film_id))

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )
    return FilmConverter.convert(film)


@router.get("/")
async def films(
        sort: str | None = Query(default=None, max_length=50),
        pg_size: int = Query(default=50, alias="page[size]"),
        pg_number: int = Query(default=1, alias="page[number]"),
        fltr: Union[UUID, None] = Query(
            default=None,
            alias="filter[genre]"
        ),
        _film_service: SearchService = Depends(get_film_service)
) -> list[FilmBase]:
    """  Returns films

    @param sort:
    @param pg_size:
    @param pg_number:
    @param fltr:
    @param _film_service:
    @return list[FilmBase]:
    """
    if fltr:
        result = await _film_service.search_nested_field(
            "genre.id",
            str(fltr),
            pg_number,
            pg_size,
            sort
        )
    else:
        result = await _film_service.list_all(pg_number, pg_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )
    return [FilmBaseConverter.convert(flm) for flm in result]
