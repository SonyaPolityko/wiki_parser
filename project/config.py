import os

from dotenv import load_dotenv

load_dotenv()

PAGE_PATH: str = "wiki/Deaths_in_2025"

URL: str = "https://en.wikipedia.org/"
HEADERS: dict = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept-Encoding": "gzip",
}
NAME_DOES_NOT_EXIST: str = "Нет имени"
PAGE_DOES_NOT_EXIST: str = "Страница не существует"

TIMEOUT: int = 5

SMTP_YA_HOST = "smtp.yandex.ru"

EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
# 86 400 = 24 часа
CHECK_INTERVAL: int = 30
NAME_PID: str = "/tmp/daemon-example.pid"
JSON_NAME: str = "december.json"

HEADER: str = "Обновлен список умерших!"

MSG_BODY: str = """Обнаружен новый пункт в списке умерших.


Ссылка: {wiki_url}

Первый абзац статьи:
{paragraph}

---
Это автоматическое сообщение от скрипта мониторинга Википедии.
"""
