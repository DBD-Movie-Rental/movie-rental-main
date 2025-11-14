from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    DateTimeField,
    DecimalField,
    ObjectIdField,
)


class Address(EmbeddedDocument):
    address = StringField(required=True, db_field="address")
    city = StringField(required=True, db_field="city")
    post_code = StringField(required=True, db_field="postCode")


class MembershipPlan(EmbeddedDocument):
    membership_type = StringField(
        required=True,
        choices=("GOLD", "SILVER", "BRONZE"),
        db_field="membershipType",
    )
    starts_on = DateTimeField(required=True, db_field="startsOn")
    ends_on = DateTimeField(db_field="endsOn")
    monthly_cost_dkk = DecimalField(required=True, db_field="monthlyCostDkk")


class RecentRental(EmbeddedDocument):
    rental_id = ObjectIdField(required=True, db_field="rentalId")
    status = StringField(
        required=True,
        choices=("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"),
    )
    rented_at_datetime = DateTimeField(required=True, db_field="rentedAtDatetime")


class Customer(Document):
    meta = {
        "collection": "customers",  # explicit collection name
        "indexes": [
            {"fields": ["customer_id"], "unique": True},  # maps to customerId db field
            "email",
        ],
    }

    # shared logical ID with MySQL customer_id
    customer_id = IntField(required=True, unique=True, db_field="customerId")

    # flat fields
    first_name = StringField(required=True, db_field="firstName")
    last_name = StringField(required=True, db_field="lastName")
    email = StringField(required=True, db_field="email")
    phone_number = StringField(db_field="phoneNumber")
    created_at = DateTimeField(required=True, db_field="createdAt")

    # embedded docs
    address = EmbeddedDocumentField(Address, required=True, db_field="address")
    membership_plan = EmbeddedDocumentField(
        MembershipPlan, required=True, db_field="membershipPlan"
    )
    recent_rentals = EmbeddedDocumentListField(
        RecentRental, db_field="recentRentals"
    )

    def to_dict(self) -> dict:
        """
        Note: This returns the "common denominator" fields
        that match the MySQL API, so your route can swap
        between MySQL and Mongo without breaking the client.
        """
        return {
            "id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
