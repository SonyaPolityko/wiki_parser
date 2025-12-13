from typing import TypedDict

class Person(TypedDict):
    name: str

type en_URL = str
type People = dict[en_URL, Person]