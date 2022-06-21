import logging
from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.schemes.film import Film, FilmBase
from core.converter import FilmBaseConverter, FilmConverter
from core.errors import FilmErrors
from services.base import DocumentService
from services.film import get_film_service


router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/search",
            response_model=list[FilmBase],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма",
            tags=['Полнотекстовый поиск'])
async def search_films(
        query: str,
        pg_size: int = Query(default=50, alias="page[size]"),
        pg_number: int = Query(default=1, alias="page[number]"),
        film_service: DocumentService = Depends(get_film_service)
) -> list[FilmBase]:
    """
    Search for 'query' in film documents

    @param query: - searching string
    @param pg_size: - max elements output
    @param pg_number: - offset
    @param _film_service: - internal parameter for work with storages
    @returns list[FilmBase]: - corresponding films
    """
    result = await film_service.search_by_field(
        path='title',
        query=query,
        page=pg_number,
        size=pg_size,
        sort=None
    )
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FilmErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [FilmBaseConverter.convert(flm) for flm in result]


@router.get('/{film_id}/',
            response_model=Film,
            summary="Детали кинопроизведения",
            description="Получение деталей по кинопроизведениям",
            response_description="Название и рейтинг фильма, участники, прочее",
            tags=['Получение документа'])
async def film_details(
        film_id: UUID,
        film_service: DocumentService = Depends(get_film_service)
) -> Film:
    """
    Get a single film document by id

    @param film_id: film unique identifier
    @param film_service: film extractor
    @returns Film:
    """
    film = await film_service.get_single(str(film_id))

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FilmErrors.NO_SUCH_ID
        )
    return FilmConverter.convert(film)


@router.get("/",
            response_model=list[FilmBase],
            summary="Список кинопроизведений",
            description="Получение всех доступных кинопроизведений",
            response_description="Список названий и идентификаторов кинопроизведений",
            tags=['Пролистывание документов'])
async def films(
        sort: str = Query(default=None, max_length=50),
        pg_size: int = Query(default=50, alias="page[size]"),
        pg_number: int = Query(default=1, alias="page[number]"),
        fltr: Union[str, None] = Query(
            default=None,
            alias="filter[genre]"
        ),
        film_service: DocumentService = Depends(get_film_service)
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
        result = await film_service.search_by_field(
            path="genre.name",
            query=str(fltr),
            page=pg_number,
            size=pg_size,
            sort=sort
        )
    else:
        result = await film_service.list_all(pg_number, pg_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FilmErrors.FILMS_NOT_FOUND
        )
    return [FilmBaseConverter.convert(flm) for flm in result]
