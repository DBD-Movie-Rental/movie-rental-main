from .base_repository import BaseRepository
from .orm_models.review_orm import Review


class ReviewRepository(BaseRepository[Review]):
    def __init__(self):
        super().__init__(Review)
