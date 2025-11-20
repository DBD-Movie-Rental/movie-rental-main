from sqlalchemy import text
import json

from .base_repository import BaseRepository
from .orm_models.rental_orm import Rental


class RentalRepository(BaseRepository[Rental]):
    def __init__(self):
        super().__init__(Rental)

    # ------------------------------------------------------------
    # Override the generic create() used by /rentals POST
    # ------------------------------------------------------------
    def create(self, data: dict):
        """
        Create a rental using the `create_rental` stored procedure.
        """

        required = ["customer_id", "inventory_item_ids"]
        missing = [f for f in required if f not in data or not data[f]]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        new_id = self.create_rental_via_proc(data)
        if not new_id:
            raise RuntimeError("create_rental returned no rental ID")

        created = self.get_by_id(new_id)
        return created or {"id": new_id}

    # ------------------------------------------------------------
    # Create rental via stored procedure
    # ------------------------------------------------------------
    def create_rental_via_proc(self, data: dict):
        """
        Calls the MySQL stored procedure create_rental().
        Returns the new rental_id.
        """
        json_items = json.dumps(data["inventory_item_ids"]) # Convert list to JSON string

        with self._SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    CALL create_rental(
                        :customer_id,
                        :employee_id,
                        :promo_code_id,
                        :inventory_items_json
                    )
                    """
                ),
                {
                    "customer_id": data["customer_id"],
                    "employee_id": data.get("employee_id"),
                    "promo_code_id": data.get("promo_code_id"),
                    "inventory_items_json": json_items,
                },
            )

            session.commit()
            row = result.fetchone()

            if row and "new_rental_id" in row._mapping:
                return row._mapping["new_rental_id"]
            return None

    # ------------------------------------------------------------
    # Make reservation creation via stored procedure
    # ------------------------------------------------------------
    def create_reservation(self, data: dict):
        required = ["customer_id", "inventory_item_ids"]
        missing = [f for f in required if f not in data or not data[f]]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        new_id = self.create_reservation_via_proc(data)
        if not new_id:
            raise RuntimeError("create_reservation returned no ID")

        created = self.get_by_id(new_id)
        return created or {"id": new_id}

    def create_reservation_via_proc(self, data: dict):
        """
        Calls the MySQL stored procedure create_reservation().
        Returns the new reservation/rental ID.
        """
        json_items = json.dumps(data["inventory_item_ids"])

        with self._SessionLocal() as session:
            result = session.execute(
                text(
                    """
                    CALL create_reservation(
                        :customer_id,
                        :employee_id,
                        :promo_code_id,
                        :inventory_items_json
                    )
                    """
                ),
                {
                    "customer_id": data["customer_id"],
                    "employee_id": data.get("employee_id"),
                    "promo_code_id": data.get("promo_code_id"),
                    "inventory_items_json": json_items,
                },
            )

            session.commit()
            row = result.fetchone()

            # Procedure returns: SELECT v_rental_id AS new_reservation_id;
            if row and "new_reservation_id" in row._mapping:
                return row._mapping["new_reservation_id"]

            # Fallback in case of used new_rental_id for both
            if row and "new_rental_id" in row._mapping:
                return row._mapping["new_rental_id"]

            return None