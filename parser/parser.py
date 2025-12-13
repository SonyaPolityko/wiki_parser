import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from config import URL
from exceptions import WikiServiceError

with open("Deaths_in_August_2023.html", "r") as file:
    src = file.read()


def get_list_href():
    list_href = []
    soup_1 = BeautifulSoup(src, "lxml")
    all_div = soup_1.find_all("div", class_="mw-heading mw-heading3")
    for div in all_div:
        ul = div.find_next_sibling("ul")
        li = ul.find_all("li")

    list_li = [
        li for div in all_div for li in div.find_next_sibling("ul").find_all("li")
    ]  # получение всех элементов li

    for li in list_li:
        href = li.find("a").get("href")
        list_href.append(href)
    return list_href


list_href = get_list_href()
en_url = URL + list_href[-1]
full_url = urljoin(URL, list_href[-1])

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept-Encoding": "gzip",
}


res = requests.get(en_url, headers=headers)
print(res.status_code)


def get_ru_url(text: str) -> str:
    """Возвращаем ссылку на страницу на русском или указанную в списке исходной страницы"""
    soup = BeautifulSoup(text, "lxml")
    try:
        ru_url = soup.find("a", class_="interlanguage-link-target", lang="ru").get(
            "href"
        )
        return ru_url
    except AttributeError:
        return full_url


def get_name(url: str):
    name = url.replace("/wiki/", "").strip()
    return name


def get_text_response(url: str) -> str:
    """Получаем HTML от сервера. При ответе != 200 возбуждается исключение WikiServiceError

    Returns: строка вида html
    """
    time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise WikiServiceError
    return response.text


def get_paragraph(text: str) -> str:
    """Получаем первый параграф"""
    soup = BeautifulSoup(text, "lxml")
    paragraph = (
        soup.find("table", class_=re.compile("infobox")).find_next_sibling("p").text
    )
    return paragraph


def get_person(url: str) -> dict:
    name = get_name(url)
    person = {
        "name": name,
    }
    return person


if __name__ == "__main__":
    text = get_text_response(full_url)
    url = get_ru_url(text)
    print(url)
    text_1 = get_text_response(url)
    paragraph = get_paragraph(text_1)
    print(paragraph)
