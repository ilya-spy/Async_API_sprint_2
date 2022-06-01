from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.errors import GenreErrors
from api.v1.schemes.converter import GenreConverter
from api.v1.schemes.genre import Genre
from services._search import SearchService
from services.genre import get_genre_service

router: APIRouter = APIRouter()


@router.get('/', response_model=list[Genre])
async def get_genres(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[int, None] = Query(default=50, alias='page[size]'),
        page_number: Union[int, None] = Query(default=1, alias='page[number]'),
        service: SearchService = Depends(get_genre_service)
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


@router.get('/search', response_model=list[Genre])
async def search_genres(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[int, None] = Query(default=50, alias='page[size]'),
        page_number: Union[int, None] = Query(default=1, alias='page[number]'),
        query: Union[str, None] = Query(default='/.*/'),
        fltr: Union[str, None] = Query(default=None),
        service: SearchService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Returns list of docs, matching 'search by name' results with filtering applied
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Genre]:
    """
    result = await service.search_field('name', query, fltr,
                                        page_number, page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GenreErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [GenreConverter.convert(gnr) for gnr in result]
