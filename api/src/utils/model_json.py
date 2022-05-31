import orjson
from pydantic import BaseModel


def _json_dumps(v, *, default):
    """
    orjson.dumps возвращает bytes, а pydantic требует unicode - декодируем
    :param v:
    :param default:
    :return:
    """
    return orjson.dumps(v, default=default).decode()


class BaseOrJsonModel(BaseModel):
    """Базовая модель с orjson сериализацией."""

    class Config:
        json_loads = orjson.loads
        json_dumps = _json_dumps
