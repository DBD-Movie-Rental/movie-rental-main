from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.genre_ogm import Genre


class GenreRepository(Neo4jBaseRepository[Genre]):
    def __init__(self):
        super().__init__(Genre, id_field="genreId")
