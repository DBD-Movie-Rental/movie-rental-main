from datetime import datetime

from .base_repository import MongoBaseRepository
from .odm_models.rental_document import Rental, RentalItemEmbedded
from .odm_models.location_document import Location


class RentalRepositoryMongo(MongoBaseRepository[Rental]):
    def __init__(self) -> None:
        super().__init__(Rental, id_field="rental_id")

    def create(self, data: dict) -> dict:
        # 1. Generate ID
        if "rental_id" not in data:
            data["rental_id"] = self._get_next_id()

        # 2. Handle Inventory Items -> Embedded Items
        inventory_ids = data.pop("inventory_item_ids", [])
        items = []
        location_id = None

        for iid in inventory_ids:
            # Find location containing this inventory item
            loc = Location.objects(inventory__inventory_item_id=iid).first()
            if loc:
                if location_id is None:
                    location_id = loc.location_id
                
                # Find the specific item in the embedded list
                inv_item = next((i for i in loc.inventory if i.inventory_item_id == iid), None)
                if inv_item:
                    items.append(RentalItemEmbedded(
                        rental_item_id=iid,  # Using inventory ID as rental item ID for simplicity
                        inventory_item_id=iid,
                        movie_id=inv_item.movie_id,
                        format_id=inv_item.format_id
                    ))

        data["items"] = items
        
        # 3. Set Location ID (inferred from items)
        if location_id:
            data["location_id"] = location_id
        elif "location_id" not in data:
            data["location_id"] = 1  # Fallback

        # 4. Set Defaults
        if "status" not in data:
            data["status"] = "OPEN"
        
        # Map schema fields to ODM fields if necessary
        # ODM has rented_at, returned_at, due_at, reserved_at
        if "rented_at_datetime" in data:
            data["rented_at"] = data.pop("rented_at_datetime")
        elif "rented_at" not in data:
            data["rented_at"] = datetime.utcnow()

        doc = self.model(**data)
        doc.save()
        return self._to_dict(doc)

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
