from .base_repository import BaseRepository
from .orm_models.movie_orm import Movie


class MovieRepository(BaseRepository[Movie]):
    def __init__(self):
        super().__init__(Movie)
