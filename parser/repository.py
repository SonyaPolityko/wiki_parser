import json
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from pathlib import Path
from typedefs import en_URL, Person, People


class Repository(ABC):
    @abstractmethod
    def _load(self, filename: str) -> None:
        """Загрузка файла"""
        ...

    @abstractmethod
    def _save(self) -> None:
        """Сохранение состояния"""
        ...


class PersonExists(Exception): ...


class JsonRepository(Repository):
    """Хранение данных в json"""

    def __init__(self, filename: str):
        self._filename = filename
        self._people = self._load()

    def _load(self) -> People:
        Path(self._filename).touch(exist_ok=True)
        with open(self._filename) as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                return {}

    def _check_person_exists(self, en_url: en_URL) -> None:
        """Выкидывается исключение PersonExists, если ссылка уже существует"""
        if en_url in self._people:
            raise PersonExists("Человек уже есть в списке")

    def add_person_info(self, en_url: en_URL, people_info: Person):
        """Добавляет информацию о людях или выбрасывает исключение"""
        self._check_person_exists(en_url)
        self._people[en_url] = people_info
        self._save()

    def _save(self):
        with open(self._filename, "w", encoding="utf-8") as f:
            return json.dump(self._people, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    people = JsonRepository("wiki_info.json")
    people.add_person_info("/wiki/Anatoliy_Sass", {"name": "Anatoliy_Sass"})
