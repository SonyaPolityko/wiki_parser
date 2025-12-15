class WikiServiceError(Exception):
    """При возникновении ошибки соединения с сервером"""

    ...


class PageNotExistsError(WikiServiceError):
    """Если страница не существует"""

    pass


class ParsingError(Exception):
    """Ошибки парсинга"""

    ...
