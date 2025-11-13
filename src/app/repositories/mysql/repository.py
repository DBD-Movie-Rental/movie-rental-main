from sqlalchemy import text
from .orm import SessionLocal, Customer

class CustomerRepository:
    def get_all_customers(self):
        with SessionLocal() as session:
            return session.query(Customer).all()

    def create_customer_via_proc(self, data):
        """
        Calls the MySQL stored procedure add_customer_with_address().
        Returns the new customer's ID.
        """
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    CALL add_customer_with_address(
                        :first_name,
                        :last_name,
                        :email,
                        :phone_number,
                        :address,
                        :city,
                        :post_code
                    )
                """),
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
        with SessionLocal() as session:
            customer = session.get(Customer, customer_id)
            if not customer:
                return False
            session.delete(customer)
            session.commit()
            return True
