from .base_repository import BaseRepository
from .orm_models.location_orm import Location


class LocationRepository(BaseRepository[Location]):
    def __init__(self):
        super().__init__(Location)
