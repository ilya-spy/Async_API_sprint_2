from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import Person, PersonFilm
from services._search import SearchService
from services.film import get_film_service
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
            detail='Persons list not available'
        )
    return result


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
            detail="Persons list query '%s' not available" % query
        )
    return result


@router.get('/{person_uuid}', response_model=Person)
async def person_details(person_uuid: str, service: SearchService = Depends(get_person_service)) -> Person:
    person = await service.get_single(person_uuid, Person)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person uuid not found')
    return person


@router.get('/{person_uuid}/films', response_model=list[PersonFilm])
async def person_films(
        person_uuid: str,
        service: SearchService = Depends(get_person_service),
        _filmService: SearchService = Depends(get_film_service)
) -> list[PersonFilm]:
    person: Person = await service.get_single(person_uuid, Person)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person uuid not found')

    return person.films
