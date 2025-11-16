from sqlalchemy import text
from .base_repository import BaseRepository
from .orm_models.customer_orm import Customer


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)

    # Make BaseRepository's generic blueprint use the stored procedure for create
    def create(self, data):  
        required_fields = [
            "first_name", 
            "last_name", 
            "email", 
            "phone_number",
            "address", 
            "city", 
            "post_code",
        ]
        missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        new_id = self.create_customer_via_proc(data)
        if not new_id:
            raise RuntimeError("Customer created, but ID could not be retrieved")
        created = self.get_by_id(new_id)
        return created or {"id": new_id}

    def create_customer_via_proc(self, data):
        """
        Calls the MySQL stored procedure add_customer_with_address().
        Returns the new customer's ID.
        """
        with self._SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    CALL add_customer_with_address(
                        :first_name,
                        :last_name,
                        :email,
                        :phone_number,
                        :address,
                        :city,
                        :post_code
                    )
                    """
                ),
                {
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "phone_number": data["phone_number"],
                    "address": data["address"],
                    "city": data["city"],
                    "post_code": data["post_code"],
                },
            )

            session.commit()

            row = result.fetchone()
            if row and "new_customer_id" in row._mapping:
                return row._mapping["new_customer_id"]
            return None

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer by id. Returns True if a row was deleted."""
        return self.delete(customer_id)
