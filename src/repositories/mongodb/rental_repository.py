from .base_repository import MongoBaseRepository
from .odm_models.rental_document import Rental


class RentalRepositoryMongo(MongoBaseRepository[Rental]):
    def __init__(self) -> None:
        super().__init__(Rental, id_field="rental_id")

        def get_details(self, rental_id: int) -> dict | None:
            """Single detailed rental: /rentals/<id>/detailed"""
            doc = self.model.objects(rental_id=rental_id).first()
            if not doc:
                return None
            return doc.to_detailed_dict()
        
        def get_all_details(self) -> list[dict]:
            """All detailed rentals: /rentals/detailed"""
            docs = self.model.objects()
            return [doc.to_detailed_dict() for doc in docs]
