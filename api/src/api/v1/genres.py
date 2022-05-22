
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, HTTPException, Depends, Query

from services.genre import GenreService, get_genre_service
from models.genre import Genre


router: APIRouter = APIRouter()


@router.get('/')
async def genres(
    sort: Union[str, None] = Query(default=None, max_length=50),
    page_size: Union[int, None] = Query(default='50', alias='page[size]'),
    page_number: Union[int, None] = Query(default='1', alias='page[number]'),
    service: GenreService = Depends(get_genre_service)
) -> list[Genre]:
    """
    Returns list of all available genres
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[FilmBase]:
    """
    result = await service.list_genres(page_number, page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genres list not available'
        )
    return result
