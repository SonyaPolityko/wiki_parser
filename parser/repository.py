import json
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from pathlib import Path

from exceptions import PersonExists, PersonNotExists
from typedefs import People, Person, en_URL


class Repository(ABC):
    @abstractmethod
    def _load(self, filename: str) -> None:
        """Загрузка файла"""
        ...

    @abstractmethod
    def _save(self) -> None:
        """Сохранение состояния"""
        ...


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

    def _check_person_exists(self, en_url: en_URL) -> bool:
        """Выкидывается исключение PersonExists, если ссылка уже существует"""
        if en_url in self._people:
            return True
        return False

    def add_person_info(self, en_url: en_URL, people_info: Person):
        """Добавляет информацию о людях или выбрасывает исключение"""
        if self._check_person_exists(en_url):
            raise PersonExists("Человек уже добавлен в список!")
        self._people[en_url] = people_info
        self._save()


    def get_person_url(self, en_url: en_URL):
        if self._check_person_exists(en_url):
            return en_url
        raise PersonNotExists('Человека нет в списке!')

    def _save(self):
        with open(self._filename, "w", encoding="utf-8") as f:
            return json.dump(self._people, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    people = JsonRepository("wiki_info.json")
    try:
        people.add_person_info("/wiki/Anatoliy_Sass", {"name": "Anatoliy_Sass"})
    except PersonExists as err:
        print(err)
    try:
        print(people.get_person_url("/wiki/Anatoliy_Sass"))
    except PersonNotExists as err:
        print(err)
