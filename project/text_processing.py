import re
import unicodedata


def clean_wikipedia_text(text: str) -> str:
    """Очистка текста из Википедии от ссылок и спецсимволов"""
    text = re.sub(r"\[\d+\]", "", text)  # все скобочные ссылки [n]
    text = remove_accents(text)
    # апострофы оставлены, так как, например, существуют английские имена, которые пишутся с ними
    # text = re.sub(r"\'+", '', text) # можно включить, если не нужны апострофы
    text = re.sub(r"\s+", " ", text).strip()  # лишние пробелы
    return text


def remove_accents(text: str) -> str:
    """Удаление ударения"""
    nfkd_form = unicodedata.normalize("NFKD", text)
    cleaned = "".join([c for c in nfkd_form if ord(c) != 769])
    return unicodedata.normalize("NFKC", cleaned)
