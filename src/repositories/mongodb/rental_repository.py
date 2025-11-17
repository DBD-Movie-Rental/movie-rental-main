from .base_repository import MongoBaseRepository
from .odm_models.rental_document import Rental


class RentalRepositoryMongo(MongoBaseRepository[Rental]):
    def __init__(self) -> None:
        super().__init__(Rental, id_field="rental_id")
