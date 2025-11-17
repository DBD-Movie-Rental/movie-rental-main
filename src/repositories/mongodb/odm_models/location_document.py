from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    BooleanField,
)


class EmployeeEmbedded(EmbeddedDocument):
    employee_id = IntField(required=True, db_field="employeeId")
    first_name = StringField(required=True, db_field="firstName")
    last_name = StringField(required=True, db_field="lastName")
    phone_number = StringField(db_field="phoneNumber")
    email = StringField(required=True, db_field="email")
    is_active = BooleanField(required=True, db_field="isActive")


class InventoryItemEmbedded(EmbeddedDocument):
    inventory_item_id = IntField(required=True, db_field="inventoryItemId")
    movie_id = IntField(required=True, db_field="movieId")
    format_id = IntField(required=True, db_field="formatId")
    status = StringField(required=True, db_field="status")  # AVAILABLE/RENTED/...


class Location(Document):
    meta = {
        "collection": "locations",
        "auto_create_index": False,
    }

    location_id = IntField(required=True, unique=True, db_field="locationId")
    address = StringField(required=True, db_field="address")
    city = StringField(required=True, db_field="city")

    employees = EmbeddedDocumentListField(EmployeeEmbedded, db_field="employees")
    inventory = EmbeddedDocumentListField(InventoryItemEmbedded, db_field="inventory")

    def to_dict(self) -> dict:
        return {
            "id": self.location_id,
            "address": self.address,
            "city": self.city,
        }

    def to_detailed_dict(self) -> dict:
        return {
            "id": self.location_id,
            "address": self.address,
            "city": self.city,
            "employees": [
                {
                    "employee_id": emp.employee_id,
                    "first_name": emp.first_name,
                    "last_name": emp.last_name,
                    "phone_number": emp.phone_number,
                    "email": emp.email,
                    "is_active": emp.is_active,
                }
                for emp in self.employees
            ],
            "inventory": [
                {
                    "inventory_item_id": item.inventory_item_id,
                    "movie_id": item.movie_id,
                    "format_id": item.format_id,
                    "status": item.status,
                }
                for item in self.inventory
            ],
        }
