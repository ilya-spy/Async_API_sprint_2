from datetime import datetime, timezone

import orjson

from state import State


async def get_last_modified(state: State, key: str) -> datetime:
    """Возвращает дату последнего изменения из хранилища состояний.

    Если не найдена, то вернет 0001-01-01 00:00:00.

    :return:
    """
    modified = await state.retrieve_state(key)
    return datetime.fromisoformat(modified) if modified else datetime.min.replace(tzinfo=timezone.utc)


json_loads = orjson.loads


def json_dumps(v, *, default):
    """
    orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    :param v:
    :param default:
    :return:
    """
    return orjson.dumps(v, default=default).decode()
