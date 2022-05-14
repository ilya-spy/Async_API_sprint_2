import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """
    orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    :param v:
    :param default:
    :return:
    """
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    """Модель фильма."""
    id: str
    title: str
    description: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
