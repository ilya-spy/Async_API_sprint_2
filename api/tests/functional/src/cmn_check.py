from typing import Optional, Type, Callable, Union, Any

from testdata.schemes.v1.genre import Genre
from testdata.models.genre import Genre as GenreModel

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1

SchemeType = Union[Genre]
ModelType = Union[GenreModel]


def page_check(doc_type: Type[SchemeType], converter: Callable[[ModelType], SchemeType], entries: list[SchemeType],
               resp_body: list[dict], page_size: int, page_number: int):
    # compute page boundaries inside index
    first_index = (page_number - 1) * page_size
    last_index = first_index + len(resp_body) - 1
    middle_index = len(resp_body) // 2

    # check page boundaries
    assert doc_type(**resp_body[0]) == converter(entries[first_index])
    assert doc_type(**resp_body[-1]) == converter(entries[last_index])
    # check some middle element
    assert doc_type(**resp_body[middle_index]) == converter(entries[first_index + middle_index])


class Changer:

    def __init__(self, index: str, field_name: str, new_val: Any, get_es_entry_updater):
        self.upd_field = get_es_entry_updater
        self.index = index
        self.new_val = new_val
        self.field_name = field_name

    async def change(self, uuid: str):
        await self.upd_field(self.index, uuid, {self.field_name: self.new_val})

    async def set(self, uuid: str, new_val: Any):
        await self.upd_field(self.index, uuid, {self.field_name: new_val})


async def cache_check(doc_type: Type[SchemeType], converter: Callable[[ModelType], SchemeType],
                      entries: list[SchemeType], uri: str, req_params: Optional[dict[str, int]],
                      request_factory, changer: Changer):
    page_id = req_params["page[number]"] if req_params["page[number]"] else DEFAULT_PAGE_NUMBER
    page_size = req_params["page[size]"] if req_params["page[size]"] else DEFAULT_PAGE_SIZE

    check_begin = (page_id - 1) * page_size
    changed_uuid = str(entries[check_begin].id)
    await changer.change(changed_uuid)
    # get from cache
    response = await request_factory(uri, req_params)
    assert response.status == 200

    # without catch data couldn't be equal
    assert doc_type(**response.body[0]) == converter(entries[check_begin])

    old_one = getattr(entries[check_begin], changer.field_name)
    await changer.set(changed_uuid, old_one)
