import orjson

json_loads = orjson.loads


def json_dumps(v, *, default):
    """
    orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    :param v:
    :param default:
    :return:
    """
    return orjson.dumps(v, default=default).decode()
