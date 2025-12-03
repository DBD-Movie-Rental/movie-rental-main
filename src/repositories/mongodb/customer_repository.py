# src/repositories/mongodb/customer_repository.py
from datetime import datetime

from .base_repository import MongoBaseRepository
from .odm_models.customer_document import Customer, Address, MembershipPlan


class CustomerRepositoryMongo(MongoBaseRepository[Customer]):
    def __init__(self) -> None:
        # Logical ID field is "customer_id" on the Document
        super().__init__(Customer, id_field="customer_id")

    def create(self, data: dict) -> dict:
        # 1. Generate ID
        if "customer_id" not in data:
            data["customer_id"] = self._get_next_id()

        # 2. Handle Address (flat input -> embedded)
        if "address" in data and isinstance(data["address"], str):
            addr_data = {
                "address_id": data["customer_id"],  # Simple ID generation
                "address": data.pop("address"),
                "city": data.pop("city"),
                "post_code": data.pop("post_code"),
            }
            data["address"] = Address(**addr_data)

        # 3. Handle MembershipPlan (default if missing)
        if "membership_plan" not in data:
            plan = MembershipPlan(
                membership_plan_id=data["customer_id"],
                membership_type="BRONZE",
                starts_on=datetime.utcnow(),
                monthly_cost_dkk=0.0,
                membership_id=3  # Assuming 3 is Bronze
            )
            data["membership_plan"] = plan

        # Default created_at if missing
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow()

        doc = self.model(**data)
        doc.save()
        return self._to_dict(doc)

    def get_details(self, customer_id: int) -> dict | None:
        """Single detailed customer: /customers/<id>/details"""
        doc = self.model.objects(customer_id=customer_id).first()
        if not doc:
            return None
        return doc.to_detailed_dict()

    def get_all_details(self) -> list[dict]:
        """All detailed customers: /customers/detailed"""
        docs = self.model.objects()
        return [doc.to_detailed_dict() for doc in docs]
