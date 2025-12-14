from abc import ABC, abstractmethod

from .parser import get_list_href, get_person
from .typedefs import EN_URL, People, Person


class Repository(ABC):
    @abstractmethod
    def _load(self) -> People:
        """Загрузка файла"""
        ...

    @abstractmethod
    def _save(self) -> None:
        """Сохранение состояния"""
        ...

    @abstractmethod
    def check_person_exists(self, en_url: EN_URL) -> bool:
        """Возвращение True, если человек уже есть в списке"""
        ...

    @abstractmethod
    def add_person_info(self, en_url: EN_URL, people_info: Person) -> None:
        """Добавление нового человека в хранилище"""
        ...


class WikiDataInitializer:
    """инициализация хранилища и прослойка между демоном и хранилищем"""

    def __init__(self, repository: Repository):
        self.repository = repository

    def save_info(self):
        """Сохранине списка в json целиком"""
        list_href = get_list_href()

        for href in list_href:
            name = get_person(href)
            self.repository.add_person_info(href, name)

    def add_new_person(self, href, name):
        self.repository.add_person_info(href, name)

    def check_person_exists(self, en_url: EN_URL) -> bool:
        """Возвращает True, если человек уже есть в списке, иначе False"""
        return self.repository.check_person_exists(en_url)
