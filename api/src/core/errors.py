from string import Template


def _create_id_error(name: str) -> str:
    return f"Requested {name} not found"


def _create_list_error(name: str) -> str:
    return "{} list not available".format(name.capitalize())


def _create_search_error(name: str) -> str:
    return "{} list query '$query' not available".format(name.capitalize())


class FilmErrors:
    NO_SUCH_ID = _create_id_error("film")
    FILMS_NOT_FOUND = _create_list_error("films")
    SEARCH_WO_RESULTS = Template(_create_search_error("films"))


class GenreErrors:
    NO_SUCH_ID = _create_id_error("genre")
    GENRES_NOT_FOUND = _create_list_error("genres")
    SEARCH_WO_RESULTS = Template(_create_search_error("genres"))


class PersonErrors:
    NO_SUCH_ID = _create_id_error("person")
    PERSONS_NOT_FOUND = _create_list_error("persons")
    SEARCH_WO_RESULTS = Template(_create_search_error("persons"))
