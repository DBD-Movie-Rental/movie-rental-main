from datetime import datetime, timedelta
from mongoengine.connection import get_db
from pymongo.write_concern import WriteConcern
from pymongo.client_session import ClientSession

from .base_repository import MongoBaseRepository
from .odm_models.rental_document import Rental, RentalItemEmbedded
from .odm_models.location_document import Location


class RentalRepositoryMongo(MongoBaseRepository[Rental]):
    def __init__(self) -> None:
        super().__init__(Rental, id_field="rental_id")

    def create_rental(
        self,
        customer_id: int,
        employee_id: int,
        promo_code_id: int,
        inventory_items: list[dict]
    ) -> dict:
        """
        Creates a rental with ACID guarantees:
        1. Checks inventory availability.
        2. Creates the rental record.
        3. Updates inventory status to 'Rented'.
        """
        with get_db().client.start_session() as session:
            return session.with_transaction(
                lambda s: self._execute_rental_creation(
                    s, customer_id, employee_id, promo_code_id, inventory_items
                ),
                write_concern=WriteConcern("majority")
            )

    def create_reservation(
        self,
        customer_id: int,
        employee_id: int,
        promo_code_id: int,
        inventory_items: list[dict]
    ) -> dict:
        """
        Creates a reservation with ACID guarantees:
        1. Checks inventory availability.
        2. Creates the rental record with status 'RESERVED'.
        3. Updates inventory status to 'Reserved'.
        """
        with get_db().client.start_session() as session:
            return session.with_transaction(
                lambda s: self._execute_reservation_creation(
                    s, customer_id, employee_id, promo_code_id, inventory_items
                ),
                write_concern=WriteConcern("majority")
            )

    def _execute_rental_creation(
        self,
        session: ClientSession,
        customer_id: int,
        employee_id: int,
        promo_code_id: int,
        inventory_items: list[dict]
    ) -> dict:
        """
        Internal business logic for creating a rental within a transaction session.
        """
        target_item_ids = [item['item_id'] for item in inventory_items]
        
        # 1. Verify Availability & Fetch Items
        # We must pass session=session to ensure we read from the snapshot
        locations = Location.objects(inventory__inventory_item_id__in=target_item_ids).session(session)
        
        found_inventory_map = {}
        primary_location = None
        
        for location in locations:
            if primary_location is None:
                primary_location = location
            
            for inventory_item in location.inventory:
                if inventory_item.inventory_item_id in target_item_ids:
                    if inventory_item.status != "1": # "1" = Available
                        raise ValueError(f"Inventory Item {inventory_item.inventory_item_id} is not available.")
                    found_inventory_map[inventory_item.inventory_item_id] = inventory_item

        if len(found_inventory_map) != len(target_item_ids):
            missing_ids = set(target_item_ids) - set(found_inventory_map.keys())
            raise ValueError(f"Inventory items not found: {missing_ids}")

        # 2. Generate New Rental ID
        last_rental = Rental.objects.order_by("-rental_id").session(session).first()
        new_rental_id = (last_rental.rental_id + 1) if last_rental else 1
        
        # 3. Create Rental Document
        rental_document = Rental(
            rental_id=new_rental_id,
            customer_id=customer_id,
            employee_id=employee_id,
            status="OPEN",
            rented_at=datetime.utcnow(),
            due_at=datetime.utcnow() + timedelta(days=7),
            location_id=primary_location.location_id if primary_location else 1
        )
        
        # Add items to rental
        current_rental_item_suffix = 1 
        for item_id in target_item_ids:
            inventory_item = found_inventory_map[item_id]
            rental_document.items.append(RentalItemEmbedded(
                rental_item_id=new_rental_id * 100 + current_rental_item_suffix,
                inventory_item_id=inventory_item.inventory_item_id,
                movie_id=inventory_item.movie_id,
                format_id=inventory_item.format_id
            ))
            current_rental_item_suffix += 1
        
        rental_document.save(session=session)

        # 4. Update Inventory Status
        for location in locations:
            is_modified = False
            for inventory_item in location.inventory:
                if inventory_item.inventory_item_id in target_item_ids:
                    inventory_item.status = "0" # 0 = Rented/Unavailable
                    is_modified = True
            
            if is_modified:
                location.save(session=session)
        
        return rental_document.to_detailed_dict()

    def _execute_reservation_creation(
        self,
        session: ClientSession,
        customer_id: int,
        employee_id: int,
        promo_code_id: int,
        inventory_items: list[dict]
    ) -> dict:
        """
        Internal business logic for creating a reservation within a transaction session.
        """
        target_item_ids = [item['item_id'] for item in inventory_items]
        
        # 1. Verify Availability
        locations = Location.objects(inventory__inventory_item_id__in=target_item_ids).session(session)
        found_inventory_map = {}
        primary_location = None
        
        for location in locations:
            if primary_location is None: primary_location = location
            for inventory_item in location.inventory:
                if inventory_item.inventory_item_id in target_item_ids:
                    if inventory_item.status != "1":
                        raise ValueError(f"Inventory Item {inventory_item.inventory_item_id} is not available.")
                    found_inventory_map[inventory_item.inventory_item_id] = inventory_item

        if len(found_inventory_map) != len(target_item_ids):
            raise ValueError("Some inventory items were not found.")

        # 2. Create Rental Document (Status RESERVED)
        last_rental = Rental.objects.order_by("-rental_id").session(session).first()
        new_rental_id = (last_rental.rental_id + 1) if last_rental else 1

        rental_document = Rental(
            rental_id=new_rental_id,
            customer_id=customer_id,
            employee_id=employee_id,
            status="RESERVED",
            reserved_at=datetime.utcnow(),
            location_id=primary_location.location_id if primary_location else 1,
        )
        
        current_rental_item_suffix = 1
        for item_id in target_item_ids:
            inventory_item = found_inventory_map[item_id]
            rental_document.items.append(RentalItemEmbedded(
                rental_item_id=new_rental_id * 100 + current_rental_item_suffix,
                inventory_item_id=inventory_item.inventory_item_id,
                movie_id=inventory_item.movie_id,
                format_id=inventory_item.format_id
            ))
            current_rental_item_suffix += 1

        rental_document.save(session=session)

        # 3. Update Inventory Status
        for location in locations:
            is_modified = False
            for inventory_item in location.inventory:
                if inventory_item.inventory_item_id in target_item_ids:
                    inventory_item.status = "0" # Reserved/Unavailable
                    is_modified = True
            if is_modified:
                location.save(session=session)
        
        return rental_document.to_detailed_dict()

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
