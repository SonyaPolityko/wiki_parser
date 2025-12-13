from repository import JsonRepository
import parser


def init_repository(filename: str) -> JsonRepository:
    repository = JsonRepository(filename)
    return repository


def save_info(repository: JsonRepository):
    list_href = parser.get_list_href()
    print(len(list_href))

    for href in list_href:
        print(href)
        name = parser.get_person(href)
        repository.add_person_info(href, name)



if __name__ == '__main__':
    repository = init_repository('wiki_december.json')
    save_info(repository)


