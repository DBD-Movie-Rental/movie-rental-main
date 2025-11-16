from .base_repository import BaseRepository
from .orm_models.fee_orm import Fee


class FeeRepository(BaseRepository[Fee]):
    def __init__(self):
        super().__init__(Fee)
