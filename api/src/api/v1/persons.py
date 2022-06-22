from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import conint

from api.v1.schemes.person import Person
from core.converter import PersonConverter
from core.errors import PersonErrors
from services.base import DocumentService
from services.person import get_person_service

router: APIRouter = APIRouter()


@router.get('/',
            response_model=list[Person],
            summary="Список персон",
            description="Получение всех доступных персон",
            response_description="Список названий и идентификаторов персон",
            tags=['Пролистывание документов'])
async def get_persons(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[conint(strict=True, gt=0), None] = Query(default=50, alias='page[size]'),
        page_number: Union[conint(strict=True, gt=0), None] = Query(default=1, alias='page[number]'),
        service: DocumentService = Depends(get_person_service)
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


@router.get('/search',
            response_model=list[Person],
            summary="Поиск персон",
            description="Полнотекстовый поиск по персон",
            response_description="Название и рейтинг персон",
            tags=['Полнотекстовый поиск'])
async def search_persons(
        sort: Union[str, None] = Query(default=None, max_length=50),
        page_size: Union[conint(strict=True, gt=0), None] = Query(default=50, alias='page[size]'),
        page_number: Union[conint(strict=True, gt=0), None] = Query(default=1, alias='page[number]'),
        query: Union[str, None] = Query(default='/.*/'),
        service: DocumentService = Depends(get_person_service)
) -> list[Person]:
    """
    Returns list of docs, matching 'search by name' results with filtering applied
    @param sort:
    @param page_size: int
    @param page_number: int
    @return list[Person]:
    """
    result = await service.search_by_field(
        path='full_name',
        query=query,
        page=page_number,
        size=page_size,
        sort=sort
    )
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PersonErrors.SEARCH_WO_RESULTS.substitute(query=query)
        )
    return [PersonConverter.convert(person) for person in result]


@router.get('/{person_uuid}',
            response_model=Person,
            summary="Детали персон",
            description="Получение деталей по персон",
            response_description="Название и рейтинг персонs, участники, прочее",
            tags=['Получение документа'])
async def person_details(person_uuid: UUID, service: DocumentService = Depends(get_person_service)) -> Person:
    person = await service.get_single(str(person_uuid))
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PersonErrors.NO_SUCH_ID
        )
    return PersonConverter.convert(person)
