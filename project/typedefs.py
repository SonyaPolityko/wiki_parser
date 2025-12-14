from typing import TypedDict


class Person(TypedDict):
    name: str


type EN_URL = str
type People = dict[EN_URL, Person]
