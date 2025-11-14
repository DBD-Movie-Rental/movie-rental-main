from datetime import datetime
from .odm_models.customer_document import Customer

class CustomerRepositoryMongo:
    def get_all_customers(self) -> list[dict]:
        customers = Customer.objects()
        return [c.to_dict() for c in customers]

    def get_customer(self, customer_id: int) -> dict | None:
        customer = Customer.objects(customer_id=customer_id).first()
        return customer.to_dict() if customer else None

    def create_customer(self, data: dict) -> int:
        customer = Customer(
            customer_id=data["customer_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data.get("phone_number"),
            created_at=datetime.utcnow(),
        )
        customer.save()
        return customer.customer_id

    def delete_customer(self, customer_id: int) -> bool:
        res = Customer.objects(customer_id=customer_id).delete()
        return res == 1  # number of docs deleted
