from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.errors import PersonErrors
from api.v1.schemes.converter import PersonConverter
from api.v1.schemes.person import Person
from services._search import SearchService
from services.person import get_person_service

router: APIRouter = APIRouter()


@router.get('/', response_model=list[Person])
async def get_persons(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[int, None] = Query(default=50, alias='page[size]'),
        page_number: Union[int, None] = Query(default=1, alias='page[number]'),
        service: SearchService = Depends(get_person_service)
) -> list[Person]:
    """
    Returns list of all available persons
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Person]:
    """
    result = await service.list_all(page_number, page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PersonErrors.PERSONS_NOT_FOUND
        )
    return [PersonConverter.convert(person) for person in result]


@router.get('/search', response_model=list[Person])
async def search_persons(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[int, None] = Query(default=50, alias='page[size]'),
        page_number: Union[int, None] = Query(default=1, alias='page[number]'),
        query: Union[str, None] = Query(default='/.*/'),
        fltr: Union[str, None] = Query(default=None),
        service: SearchService = Depends(get_person_service)
) -> list[Person]:
    """
    Returns list of docs, matching 'search by name' results with filtering applied
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Person]:
    """
    result = await service.search_field('full_name', query, fltr,
                                        page_number, page_size, sort)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PersonErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [PersonConverter.convert(person) for person in result]


@router.get('/{person_uuid}', response_model=Person)
async def person_details(person_uuid: str, service: SearchService = Depends(get_person_service)) -> Person:
    person = await service.get_single(person_uuid)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PersonErrors.NO_SUCH_ID
        )
    return PersonConverter.convert(person)
