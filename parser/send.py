import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config import SMTP_YA_HOST
from loguru import logger

logger.add('log_mail.json', format='{time} {level} {message}',
           level= 'DEBUG', rotation='1 week', compression='zip',
           serialize=True)
load_dotenv()

def compose_msg(person_name: str, wiki_url: str, paragraph: str) -> str:
    """Создание сообщения"""
    body = f"""Обнаружен новый пункт в списке умерших.

Имя: {person_name}
Ссылка: {wiki_url}

Первый абзац статьи:
{paragraph}

---
Это автоматическое сообщение от скрипта мониторинга Википедии.
"""
    return body


def send_wiki_email(recipients_emails: list[str], mg_text: str):
    """Создание сервера и отправка сообщения"""
    login = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')

    if not login or not password:
        logger.error("Не заданы EMAIL_SENDER или EMAIL_PASSWORD")
        return False

    msg = MIMEText(f'{mg_text}', 'plain', 'utf-8')
    msg['Subject'] = Header('Обновлен список умерших!', 'utf-8')
    msg['From'] = login
    msg['To'] = ', '.join(recipients_emails)


    with smtplib.SMTP(SMTP_YA_HOST, 587, timeout=10) as server:
        try:
            server.starttls()
            server.login(login, password)
            server.sendmail(msg['From'], recipients_emails, msg.as_string())
            logger.info(f'Сообщение успешно отправлено на адрес {recipients_emails}')
            return True
        except Exception as err:
            logger.error(err)
            return False


if __name__ == '__main__':
    msg = compose_msg('Phillip_Naumenko', 'https://en.wikipedia.org/wiki/Phillip_Naumenko', 'Philipp Anatolyevich Naumenko (Russian: Фили́пп Анато́льевич Нау́менко; 28 December 1985 – 13 December 2025) was a Russian politician')
    send_wiki_email(recipients_emails=[os.getenv('EMAIL_RECIPIENT')], mg_text=msg)


