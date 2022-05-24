from datetime import datetime, timezone

from etl.state import State


async def get_last_modified(state: State, key: str) -> datetime:
    """Возвращает дату последнего изменения из хранилища состояний.

    Если не найдена, то вернет 0001-01-01 00:00:00.

    :return:
    """
    modified = await state.retrieve_state(key)
    return datetime.fromisoformat(modified) if modified else datetime.min.replace(tzinfo=timezone.utc)
