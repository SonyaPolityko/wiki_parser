import re
import time
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from config import URL
from exceptions import PageNotExistsError, WikiServiceError
from typedefs import Person

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept-Encoding": "gzip",
}


def get_text_response(url: str) -> str:
    """Получаем HTML от сервера. При ответе != 200 возбуждается исключение WikiServiceError

    Returns: строка вида html
    """
    # time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise WikiServiceError
    return response.text


def main_html():
    full_url = urljoin(URL, "wiki/Deaths_in_2025")
    src = get_text_response(full_url)
    return src


def get_list_href() -> list[str]:
    """Возвращает список относительных ссылок"""
    src = main_html()

    list_href = []
    soup = BeautifulSoup(src, "lxml")
    all_div = soup.find_all("div", class_="mw-heading mw-heading3")

    list_li = [
        li for div in all_div for li in div.find_next_sibling("ul").find_all("li")
    ]  # получение всех элементов li

    for li in list_li:
        href = li.find("a").get("href")
        if href in list_href:
            continue
        list_href.append(href)

    return list_href


def get_full_url(href: str) -> str:
    """Собирает полный URL"""
    if "action=edit&redlink=1" in href:
        raise PageNotExistsError
    full_url = urljoin(URL, href)
    return full_url


def get_ru_url(text: str) -> str:
    """Возвращает ссылку на страницу на русском или указанную в списке исходной страницы"""
    soup = BeautifulSoup(text, "lxml")
    try:
        ru_url = soup.find("a", class_="interlanguage-link-target", lang="ru").get(
            "href"
        )
        return ru_url
    except AttributeError:
        return full_url


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

    return "Нет имени"


def get_paragraph(text: str) -> str:
    """Получаем первый параграф"""
    soup = BeautifulSoup(text, "lxml")
    try:
        paragraph = (
            soup.find("table", class_=re.compile("infobox"))
            .find_next_sibling("p")
            .get_text(strip=True)
        )
        if not paragraph:
            paragraph = (
                soup.find("table", class_=re.compile("infobox"))
                .find_next_sibling("p")
                .find_next_sibling("p")
                .get_text(strip=True)
            )
    except AttributeError:
        paragraph = (
            soup.find("div", class_="mw-content-ltr mw-parser-output")
            .find("p")
            .get_text(strip=True)
        )
    return clean_wikipedia_text(paragraph)


def clean_wikipedia_text(text: str) -> str:
    """Очистка текста из Википедии от ссылок и спецсимволов"""
    text = re.sub(r"\[\d+\]", "", text)  # все скобочные ссылки [n]
    text = re.sub(r"\s+", " ", text).strip()  # лишние пробелы
    text = remove_accents(text)
    return text


def remove_accents(text: str) -> str:
    """Удаление ударения"""
    nfkd_form = unicodedata.normalize("NFKD", text)
    cleaned = "".join([c for c in nfkd_form if ord(c) != 769])
    return unicodedata.normalize("NFKC", cleaned)


def get_person(url: str) -> Person:
    """Возвращает словарь {name: name}"""
    name = get_name(url)
    person = {
        "name": name,
    }
    return person


if __name__ == "__main__":
    list_href = get_list_href()
    for i in range(10):
        time.sleep(1)
        try:
            full_url = get_full_url(list_href[i])
            text = get_text_response(full_url)
            url = get_ru_url(text)
            print(url)
            text_1 = get_text_response(url)
            paragraph = get_paragraph(text_1)
            print(paragraph)
        except PageNotExistsError:
            print("Страница не существует!")
