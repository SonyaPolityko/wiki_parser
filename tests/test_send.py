import os

from project.send import compose_msg, send_wiki_email


def test_compose_message():
    """Cборка сообщения"""
    url = "https://ru.wikipedia.org/wiki/John_Doe"
    paragraph = "John Doe (род. 1950) — американский учёный."

    message = compose_msg(url, paragraph)

    assert url in message
    assert paragraph in message


def test_missing_credentials(mocker):
    """Нет настроенных данных"""
    mocker.patch.dict(os.environ, {}, clear=True)

    result = send_wiki_email("recipient@example.com", "Test")
    assert result is False
