import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from dotenv import load_dotenv
from loguru import logger

from .config import EMAIL_RECIPIENT, HEADER, MSG_BODY, SMTP_YA_HOST

load_dotenv()


def compose_msg(wiki_url: str, paragraph: str) -> str:
    """Создание текста для письма"""

    body = MSG_BODY.format(wiki_url=wiki_url, paragraph=paragraph)
    return body


def send_wiki_email(recipient_email: str, mg_text: str):
    """Создание сервера и отправка сообщения"""
    login = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not login or not password:
        logger.error("Не заданы EMAIL_SENDER или EMAIL_PASSWORD")
        return False

    msg = MIMEText(f"{mg_text}", "plain", "utf-8")
    msg["Subject"] = Header(HEADER, "utf-8").encode()
    msg["From"] = login

    msg["To"] = recipient_email

    with smtplib.SMTP(SMTP_YA_HOST, 587, timeout=10) as server:
        try:
            server.starttls()
            server.login(login, password)
            server.sendmail(msg["From"], recipient_email, msg.as_string())
            logger.info(f"Сообщение успешно отправлено на адрес {recipient_email}")
            return True
        except Exception as err:
            logger.error(err)
            return False


if __name__ == "__main__":
    msg = compose_msg(
        "https://en.wikipedia.org/wiki/Phillip_Naumenko",
        "Philipp Anatolyevich Naumenko (Russian: Фили́пп Анато́льевич Нау́менко; 28 December 1985 – 13 December 2025) was a Russian politician",  # noqa: E501
    )
    send_wiki_email(recipient_email=EMAIL_RECIPIENT, mg_text=msg)
