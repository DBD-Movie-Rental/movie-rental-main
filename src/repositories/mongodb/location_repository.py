from .base_repository import MongoBaseRepository
from .odm_models.location_document import Location


class LocationRepositoryMongo(MongoBaseRepository[Location]):
    def __init__(self) -> None:
        super().__init__(Location, id_field="location_id")

    def get_details(self, location_id: int) -> dict | None:
        """Single detailed location: /locations/<id>/detailed"""
        doc = self.model.objects(location_id=location_id).first()
        if not doc:
            return None
        return doc.to_detailed_dict()
    
    def get_all_details(self) -> list[dict]:
        """All detailed locations: /locations/detailed"""
        docs = self.model.objects()
        return [doc.to_detailed_dict() for doc in docs]