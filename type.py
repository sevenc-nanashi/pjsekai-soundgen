from typing import TypedDict


class SRL(TypedDict):
    hash: str
    url: str


class Level(TypedDict):
    artists: str
    author: str
    bgm: SRL
    cover: SRL
    data: SRL
    name: str
    rating: int
    title: str


class LevelResponse(TypedDict):
    description: str
    recommended: list[Level]


class LevelList(TypedDict):
    pageCount: int
    items: list[Level]


class LevelEntityData(TypedDict):
    index: int
    values: list[int]


class LevelEntity(TypedDict):
    archetype: int
    data: LevelEntityData


class LevelData(TypedDict):
    entities: list[LevelEntity]
