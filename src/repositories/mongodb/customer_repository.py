# src/repositories/mongodb/customer_repository.py
from datetime import datetime

from .base_repository import MongoBaseRepository
from .odm_models.customer_document import Customer


class CustomerRepositoryMongo(MongoBaseRepository[Customer]):
    def __init__(self) -> None:
        # Logical ID field is "customer_id" on the Document
        super().__init__(Customer, id_field="customer_id")

    def create(self, data: dict) -> dict:
        """
        For now: require the full customer payload that matches the ODM.
        If you're only doing reads from Mongo in the API, you can even
        raise NotImplementedError here.
        """
        # Default created_at if missing
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow()

        doc = self.model(**data)
        doc.save()
        return self._to_dict(doc)

    def get_details(self, customer_id: int) -> dict | None:
        doc = self.model.objects(customer_id=customer_id).first()
        if not doc:
            return None
        return doc.to_detailed_dict()
