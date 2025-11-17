from .base_repository import MongoBaseRepository
from .odm_models.location_document import Location


class LocationRepositoryMongo(MongoBaseRepository[Location]):
    def __init__(self) -> None:
        super().__init__(Location, id_field="location_id")
