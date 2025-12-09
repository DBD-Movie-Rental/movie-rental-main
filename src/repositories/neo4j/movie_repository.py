from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.movie_ogm import Movie


class MovieRepository(Neo4jBaseRepository[Movie]):
    def __init__(self):
        super().__init__(Movie, id_field="movieId")
