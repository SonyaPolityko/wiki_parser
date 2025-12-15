import re
import time
from collections.abc import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import HEADERS, NAME_DOES_NOT_EXIST, PAGE_PATH, TIMEOUT, URL
from .exceptions import PageNotExistsError, ParsingError, WikiServiceError
from .text_processing import clean_wikipedia_text
from .typedefs import Person


def get_text_response(url: str) -> str:
    """Получаем HTML от сервера. При ответе != 200 возбуждается исключение WikiServiceError
    Returns: строка вида html
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        return response.text
    except requests.exceptions.ConnectionError:
        raise WikiServiceError  # noqa: B904


def main_html():
    """Загрузка главной страницы со списками"""
    full_url = urljoin(URL, PAGE_PATH)
    return get_text_response(full_url)


def get_list_href() -> Generator[str]:
    """Возвращает генератор относительных ссылок"""
    try:
        src = main_html()

        soup = BeautifulSoup(src, "lxml")
        all_div = soup.find_all("div", class_="mw-heading mw-heading3")
        gen_li = (
            li for div in all_div for li in div.find_next_sibling("ul").find_all("li")
        )  # получение генератора всех элементов li
        gen_href = (str(li.find("a").get("href")) for li in gen_li)  # генератор ссылок
        return gen_href
    except AttributeError:
        raise ParsingError('Ошибка при парсинге ссылок')  # noqa: B904


def get_full_url(href: str) -> str:
    """Возвращает полный URL. Возбуждает исключение, если ссылки не существует"""

    if "redlink=1" in href:
        raise PageNotExistsError
    full_url = urljoin(URL, href)
    return full_url


def get_ru_url(text: str, original_url: str) -> str:
    """Возвращает ссылку на страницу на русском или оригинальрную, указанную в списке исходной страницы"""
    ru_url = original_url
    try:
        soup = BeautifulSoup(text, "lxml")
        tag_a = soup.find("a", class_="interlanguage-link-target", lang="ru")
        if tag_a:
            ru_url = tag_a.get("href")
        return str(ru_url)
    except Exception:
        return original_url


def get_name(url: str) -> str:
    """Извлекает имя из URL Wikipedia."""
    pattern = r"/wiki/([^/&\?#]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)

    pattern2 = r"title=([^&]+)"
    match = re.search(pattern2, url)
    if match:
        return match.group(1)

    return NAME_DOES_NOT_EXIST


def _parse_next_p(first_p: BeautifulSoup):
    """Парсинг следующего параграфа, если первый пустой"""
    next_p = first_p.find_next_sibling("p")
    if next_p:
        paragraph = next_p.get_text()
        return paragraph


def _parse_paragraph(soup: BeautifulSoup):
    """Собираем текст в первом параграфе"""
    infobox = soup.find("table", class_=re.compile("infobox"))
    if infobox:
        first_p = infobox.find_next_sibling("p")
        if first_p:
            paragraph = first_p.get_text()
            if not paragraph:
                paragraph = _parse_next_p(first_p)
            return paragraph
    else:
        paragraph = soup.find("div", class_="mw-content-ltr mw-parser-output").find("p").get_text()
        return paragraph


def get_paragraph(text: str) -> str:
    """Получаем первый параграф"""
    soup = BeautifulSoup(text, "lxml")
    try:
        paragraph = _parse_paragraph(soup)
    except AttributeError:
        paragraph = ""

    return clean_wikipedia_text(paragraph)


def get_person(url: str) -> Person:
    """Возвращает словарь {name: name}"""
    name = get_name(url)
    return Person(name=name)


if __name__ == "__main__":
    list_href = get_list_href()
    for _ in range(5, 9):
        time.sleep(1)
        try:
            url = get_full_url(next(list_href))
            text = get_text_response(url)
            url = get_ru_url(text, url)
            print(url)
            text_1 = get_text_response(url)
            paragraph = get_paragraph(text_1)
            print(paragraph)
        except PageNotExistsError:
            print("Страница не существует!")
