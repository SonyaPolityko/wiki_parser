import pytest

from project.exceptions import PageNotExistsError
from project.parser import (
    clean_wikipedia_text,
    get_full_url,
    get_list_href,
    get_name,
    get_paragraph,
    get_ru_url,
)
from project.text_processing import remove_accents


@pytest.fixture
def sample_wiki_html():
    """Пример HTML страницы Википедии."""
    return """
    <html>
        <div class="mw-heading mw-heading3">
            <h3>January</h3>
        </div>
        <ul>
            <li><a href="/wiki/John_Doe">John Doe</a></li>
            <li><a href="/wiki/Jane_Smith">Jane Smith</a></li>
        </ul>
        <div class="mw-heading mw-heading3">
            <h3>February</h3>
        </div>
        <ul>
            <li><a href="/wiki/Alice_Johnson">Alice Johnson</a></li>
        </ul>
    </html>
    """


@pytest.fixture
def sample_person_html():
    """HTML страницы человека с русской версией."""
    return """
    <html>
        <head>
            <link rel="alternate" hreflang="ru" href="https://ru.wikipedia.org/wiki/Иван_Иванов" />
        </head>
        <body>
            <a class="interlanguage-link-target" lang="ru" href="https://ru.wikipedia.org/wiki/Иван_Иванов">Русский</a>
            <table class="infobox">
                <tr><td>Инфобокс</td></tr>
            </table>
            <p>Иван Иванов (род. 1970) — российский учёный[1]</p>
            <p>Второй параграф.</p>
        </body>
    </html>
    """


def test_extract_links(mocker, sample_wiki_html):
    """Извлечение ссылок из HTML."""
    mocker.patch("project.parser.main_html", return_value=sample_wiki_html)

    links = list(get_list_href())

    assert len(links) == 3
    assert "/wiki/John_Doe" in links
    assert "/wiki/Jane_Smith" in links
    assert "/wiki/Alice_Johnson" in links


def test_skip_redlinks(mocker):
    """Пропуск redlinks."""
    html = """
    <div class="mw-heading mw-heading3">
        <h3>Test</h3>
    </div>
    <ul>
        <li><a href="/w/index.php?title=Test&action=edit&redlink=1">Test</a></li>
        <li><a href="/wiki/Valid">Valid</a></li>
    </ul>
    """
    mocker.patch("project.parser.main_html", return_value=html)

    links = list(get_list_href())

    assert len(links) == 2
    assert "/wiki/Valid" in links
    assert "/w/index.php?title=Test&action=edit&redlink=1" in links


def test_valid_href():
    """Валидная ссылка."""
    url = get_full_url("/wiki/Test")
    assert url == "https://en.wikipedia.org/wiki/Test"


def test_redlink_exception():
    """Исключение для redlink."""
    with pytest.raises(PageNotExistsError):
        get_full_url("/w/index.php?title=Test&redlink=1")


def test_russian_version_found(sample_person_html):
    """Найдена русская версия."""
    result = get_ru_url(sample_person_html, "https://en.wikipedia.org/wiki/Ivan_Ivanov")
    assert result == "https://ru.wikipedia.org/wiki/Иван_Иванов"


def test_no_russian_version():
    """Русская версия не найдена."""
    html = "<html><body>No Russian link</body></html>"
    original_url = "https://en.wikipedia.org/wiki/Test"

    result = get_ru_url(html, original_url)
    assert result == original_url


def test_get_name_from_standard_wiki_url():
    """Стандартная wiki ссылка."""
    name = get_name("https://en.wikipedia.org/wiki/John_Doe")
    assert name == "John_Doe"


def test_extract_from_infobox(sample_person_html):
    """Извлечение параграфа после инфобокса."""
    paragraph = get_paragraph(sample_person_html)
    assert paragraph == "Иван Иванов (род. 1970) — российский учёный"


def test_extract_from_content_div():
    """Извлечение из основного контента."""
    html = """
    <html>
        <div class="mw-content-ltr mw-parser-output">
            <p>Это первый параграф статьи.</p>
            <p>Второй параграф.</p>
        </div>
    </html>
    """
    paragraph = get_paragraph(html)
    assert paragraph == "Это первый параграф статьи."


def test_empty_page():
    """Пустая страница."""
    paragraph = get_paragraph("<html></html>")
    assert paragraph == ""


def test_remove_footnotes():
    """Удаление сносок."""
    text = "Текст со сносками[1][2][3] и продолжение."
    cleaned = clean_wikipedia_text(text)
    assert "[1]" not in cleaned
    assert "[2]" not in cleaned
    assert "[3]" not in cleaned


def test_remove_accents():
    """Удаление ударений."""
    text = "Словó с удáрением"
    cleaned = remove_accents(text)
    assert "удaрением" in cleaned.lower()
