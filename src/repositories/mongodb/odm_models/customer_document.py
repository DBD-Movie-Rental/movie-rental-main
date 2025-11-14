from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    DateTimeField,
    DecimalField,
)


class Address(EmbeddedDocument):
    # MySQL address.address_id
    address_id = IntField(required=True, db_field="addressId")

    address = StringField(required=True, db_field="address")
    city = StringField(required=True, db_field="city")
    post_code = StringField(required=True, db_field="postCode")


class MembershipPlan(EmbeddedDocument):
    # MySQL membership_plan.membership_plan_id
    membership_plan_id = IntField(required=True, db_field="membershipPlanId")

    # MySQL membership.membership (enum)
    membership_type = StringField(
        required=True,
        choices=("GOLD", "SILVER", "BRONZE"),
        db_field="membershipType",
    )

    starts_on = DateTimeField(required=True, db_field="startsOn")
    ends_on = DateTimeField(db_field="endsOn")

    # MySQL membership_plan.monthly_cost
    monthly_cost_dkk = DecimalField(required=True, db_field="monthlyCostDkk")

    # MySQL membership.membership_id
    membership_id = IntField(required=True, db_field="membershipId")


class RecentRental(EmbeddedDocument):
    # MySQL rental.rental_id
    rental_id = IntField(required=True, db_field="rentalId")

    status = StringField(
        required=True,
        choices=("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"),
        db_field="status",
    )
    rented_at_datetime = DateTimeField(required=True, db_field="rentedAtDatetime")


class Customer(Document):
    meta = {
        "collection": "customers",  # explicit collection name
        "indexes": [
            {"fields": ["customer_id"], "unique": True},  # customerId in Mongo
            "email",
        ],
    }

    # Shared logical ID with MySQL customer.customer_id
    customer_id = IntField(required=True, unique=True, db_field="customerId")

    # Flat fields
    first_name = StringField(required=True, db_field="firstName")
    last_name = StringField(required=True, db_field="lastName")
    email = StringField(required=True, db_field="email")
    phone_number = StringField(db_field="phoneNumber")
    created_at = DateTimeField(required=True, db_field="createdAt")

    # Embedded documents
    address = EmbeddedDocumentField(Address, required=True, db_field="address")
    membership_plan = EmbeddedDocumentField(
        MembershipPlan, required=True, db_field="membershipPlan"
    )
    recent_rentals = EmbeddedDocumentListField(
        RecentRental, db_field="recentRentals"
    )

    def to_dict(self) -> dict:
        """
        Returns the common fields that match the MySQL-backed API.
        This lets your routes switch repository (MySQL vs Mongo)
        without changing the response shape.
        """
        return {
            "id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
