import json
from json.decoder import JSONDecodeError
from pathlib import Path

from .init_repository import Repository
from .typedefs import EN_URL, People, Person


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

    def check_person_exists(self, en_url: EN_URL) -> bool:
        """Возвращается True, если ссылка уже существует, иначе False"""
        return en_url in self._people

    def add_person_info(self, en_url: EN_URL, people_info: Person) -> None:
        """Добавляет информацию о человеке, если его нет в хранилище"""
        if not self.check_person_exists(en_url):
            self._people[en_url] = people_info
            self._save()

    def _save(self):
        with open(self._filename, "w", encoding="utf-8") as f:
            return json.dump(self._people, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    people = JsonRepository("wiki_info.json")
    people.add_person_info("/wiki/Anatoliy_Sass", {"name": "Anatoliy_Sass"})
