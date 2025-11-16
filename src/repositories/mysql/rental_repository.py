from .base_repository import BaseRepository
from .orm_models.rental_orm import Rental


class RentalRepository(BaseRepository[Rental]):
    def __init__(self):
        super().__init__(Rental)
