class WikiServiceError(Exception):
    """Ответ сервера, отличный от 200"""

    ...


class PageNotExistsError(WikiServiceError):
    """Если страница не существует"""

    pass


class ParsingError(Exception):
    """Ошибки парсинга"""

    ...
