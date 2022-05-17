import logging
from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.films_schemas import FilmDetails, FilmBase
from services.film import FilmService, get_film_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/search")
async def search_films(
        query: Union[str, None],
        pg_size: Union[int, None] = Query(
            default=None,
            alias="page[size]"
        ),
        pg_number: Union[int, None] = Query(
            default=None,
            alias="page[number]"
        ),
        _film_service: FilmService = Depends(get_film_service)
) -> list[FilmBase]:
    """
    Search for 'query' in films
    @param query: - searching string
    @param pg_size: - max elements output
    @param pg_number: - offset
    @param _film_service: - internal parameter for work with storages
    @return list[FilmBase]: - corresponding films
    """
    result = await _film_service.search(query, pg_number, pg_size)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )
    return [
        FilmBase(
            uuid=flm.id,
            title=flm.title,
            imdb_rating=flm.imdb_rating
        )
        for flm in result
    ]


@router.get('/{film_id}/', response_model=FilmDetails)
async def film_details(
        film_id: UUID,
        film_service: FilmService = Depends(get_film_service)
) -> FilmDetails:
    """

    @param film_id: film unique identifier
    @param film_service: film extractor
    @return FilmDetails:
    """
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )
    return FilmDetails(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get("/")
async def films(
        sort: Union[str, None] = Query(default=None, max_length=50),
        pg_size: Union[int, None] = Query(default=None, alias="page[size]"),
        pg_number: Union[int, None] = Query(
            default=None,
            alias="page[number]"
        ),
        fltr: Union[str, None] = Query(
            default=None,
            alias="filter[genre]",
            max_length=50
        ),
        _film_service: FilmService = Depends(get_film_service)
) -> list[FilmBase]:
    """  Returns films

    @param sort:
    @param pg_size:
    @param pg_number:
    @param fltr:
    @param _film_service:
    @return list[FilmBase]:
    """
    result = await _film_service.get_films(pg_number, pg_size, fltr, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )
    return [
        FilmBase(uuid=flm.id, title=flm.title, imdb_rating=flm.imdb_rating)
        for flm in result
    ]
