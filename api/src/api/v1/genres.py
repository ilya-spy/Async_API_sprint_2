
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, HTTPException, Depends, Query

from services.genre import get_genre_service
from services._search import SearchService

from models.genre import Genre
from models.film import Film


router: APIRouter = APIRouter()


@router.get('/')
async def get_genres(
            sort: Union[str, None] = Query(default=None, max_length=50),
            page_size: Union[int, None] = Query(default=50, alias='page[size]'),
            page_number: Union[int, None] = Query(default=1, alias='page[number]'),
            service: SearchService = Depends(get_genre_service)
) -> list[Film]:
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
            detail='Genres list not available'
        )
    return result


@router.get('/search')
async def search_genres(
            sort: Union[str, None] = Query(default=None, max_length=50),
            page_size: Union[int, None] = Query(default=50, alias='page[size]'),
            page_number: Union[int, None] = Query(default=1, alias='page[number]'),
            query: Union[str, None] = Query(default=None),
            fltr: Union[str, None] = Query(default=None),
            service: SearchService = Depends(get_genre_service)
) -> list[Film]:
    """
    Returns list of docs, matching 'search by name' results with filtering applied
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Genre]:
    """
    result = await service.search_field('title', query, fltr,
                                    page_number, page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genres list query not available'
        )
    return result
