from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.schemes.genre import Genre
from api.v1.params.pagination import PaginationParams

from core.converter import GenreConverter
from core.errors import GenreErrors
from services.base import DocumentService
from services.genre import get_genre_service

router: APIRouter = APIRouter()


@router.get('/',
            response_model=list[Genre],
            summary="Список жанров",
            description="Получение всех доступных жанров",
            response_description="Список названий и идентификаторов жанров",
            tags=['Пролистывание документов'])
async def get_genres(
        sort: Union[str, None] = Query(default=None, max_length=50),
        pagination: PaginationParams = Depends(PaginationParams),
        service: DocumentService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Returns list of all available genres
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Genre]:
    """
    result = await service.list_all(pagination.page_number, pagination.page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GenreErrors.GENRES_NOT_FOUND
        )
    return [GenreConverter.convert(gnr) for gnr in result]


@router.get('/search',
            response_model=list[Genre],
            summary="Поиск жанров",
            description="Полнотекстовый поиск по жанрам",
            response_description="Название и рейтинг жанра",
            tags=['Полнотекстовый поиск'])
async def search_genres(
        sort: Union[str, None] = Query(default=None, max_length=50),
        pagination: PaginationParams = Depends(PaginationParams),
        query: Union[str, None] = Query(default='/.*/'),
        service: DocumentService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Returns list of docs, matching 'search by name' results with filtering applied

    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Genre]:
    """
    result = await service.search_by_field(
        path='name',
        query=query,
        page=pagination.page_number,
        size=pagination.page_size,
        sort=sort)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GenreErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [GenreConverter.convert(gnr) for gnr in result]


@router.get('/{genre_id}/', response_model=Genre)
async def genre_details(
        genre_id: UUID,
        _genre_service: DocumentService = Depends(get_genre_service)
) -> Genre:
    """

    @param genre_id: genre unique identifier
    @param _genre_service: genre extractor
    @return Genre:
    """
    genre = await _genre_service.get_single(str(genre_id))

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GenreErrors.NO_SUCH_ID
        )
    return GenreConverter.convert(genre)
