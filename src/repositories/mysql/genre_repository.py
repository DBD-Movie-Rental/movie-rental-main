from .base_repository import BaseRepository
from .orm_models.genre_orm import Genre


class GenreRepository(BaseRepository[Genre]):
    def __init__(self):
        super().__init__(Genre)
