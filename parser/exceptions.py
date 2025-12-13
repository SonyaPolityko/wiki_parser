class PersonExists(Exception): ...


class PersonNotExists(Exception): ...


class WikiServiceError(Exception):
    """Ответ сервера, отличный от 200"""

    ...


class PageNotExistsError(WikiServiceError):
    """Если страница не существует"""

    pass
