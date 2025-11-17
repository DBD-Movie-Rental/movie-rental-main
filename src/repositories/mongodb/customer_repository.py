# src/repositories/mongodb/customer_repository.py
from datetime import datetime

from .base_repository import MongoBaseRepository
from .odm_models.customer_document import Customer


class CustomerRepositoryMongo(MongoBaseRepository[Customer]):
    def __init__(self):
        # Lookups by logical customer_id (shared with MySQL)
        super().__init__(Customer, id_field="customer_id")

    def create(self, data: dict) -> dict:
        """
        Override create to:
          - validate required fields
          - set created_at if not provided
          - optionally handle embedded docs
        """
        required = ["first_name", "last_name", "email", "phone_number"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        payload = {
            "customer_id": data.get("customer_id"),   # may come from migration or API
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "phone_number": data["phone_number"],
            "created_at": data.get("created_at") or datetime.utcnow(),
        }

        # TODO (if you want): map nested address / membership_plan from data
        # e.g. payload["address"] = Address(...)

        doc = Customer(**payload)
        doc.save()
        return doc.to_dict()
