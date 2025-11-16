from .base_repository import BaseRepository
from .orm_models.address_orm import Address


class AddressRepository(BaseRepository[Address]):
    def __init__(self):
        super().__init__(Address)
