from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import conint

from api.v1.schemes.genre import Genre
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
        page_size: Union[conint(strict=True, gt=0), None] = Query(default=50, alias='page[size]'),
        page_number: Union[conint(strict=True, gt=0), None] = Query(default=1, alias='page[number]'),
        service: DocumentService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Returns list of all available genres
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Genre]:
    """
    result = await service.list_all(page_number, page_size, sort)
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
        page_size: Union[conint(strict=True, gt=0), None] = Query(default=50, alias='page[size]'),
        page_number: Union[conint(strict=True, gt=0), None] = Query(default=1, alias='page[number]'),
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
        page=page_number,
        size=page_size,
        sort=sort)

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GenreErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [GenreConverter.convert(gnr) for gnr in result]
