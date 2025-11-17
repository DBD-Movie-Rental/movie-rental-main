from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    DateTimeField,
    Decimal128Field as DecimalField,
)


class Address(EmbeddedDocument):
    address_id = IntField(required=True, db_field="addressId")
    address = StringField(required=True, db_field="address")
    city = StringField(required=True, db_field="city")
    post_code = StringField(required=True, db_field="postCode")


class MembershipPlan(EmbeddedDocument):
    membership_plan_id = IntField(required=True, db_field="membershipPlanId")
    membership_type = StringField(
        required=True,
        choices=("GOLD", "SILVER", "BRONZE"),
        db_field="membershipType",
    )
    starts_on = DateTimeField(required=True, db_field="startsOn")
    ends_on = DateTimeField(db_field="endsOn")
    monthly_cost_dkk = DecimalField(required=True, db_field="monthlyCostDkk")
    membership_id = IntField(required=True, db_field="membershipId")


class RecentRental(EmbeddedDocument):
    rental_id = IntField(required=True, db_field="rentalId")
    status = StringField(
        required=True,
        choices=("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"),
        db_field="status",
    )
    rented_at_datetime = DateTimeField(required=True, db_field="rentedAtDatetime")


class Customer(Document):
    meta = {
        "collection": "customers",
        "auto_create_index": False, 
    }

    # Shared logical ID with MySQL customer.customer_id
    customer_id = IntField(required=True, unique=True, db_field="customerId")
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
        """
        return {
            "id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_detailed_dict(self) -> dict:
        """
        Returns all fields including embedded documents.
        """
        return {
            "id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "address": {
                "address_id": self.address.address_id,
                "address": self.address.address,
                "city": self.address.city,
                "post_code": self.address.post_code,
            } if self.address else None,
            "membership_plan": {
                "membership_plan_id": self.membership_plan.membership_plan_id,
                "membership_type": self.membership_plan.membership_type,
                "starts_on": self.membership_plan.starts_on.isoformat() if self.membership_plan.starts_on else None,
                "ends_on": self.membership_plan.ends_on.isoformat() if self.membership_plan.ends_on else None,
                "monthly_cost_dkk": str(self.membership_plan.monthly_cost_dkk) if self.membership_plan.monthly_cost_dkk else None,
                "membership_id": self.membership_plan.membership_id,
            } if self.membership_plan else None,
            "recent_rentals": [
                {
                    "rental_id": rental.rental_id,
                    "status": rental.status,
                    "rented_at_datetime": rental.rented_at_datetime.isoformat() if rental.rented_at_datetime else None,
                } for rental in self.recent_rentals
            ] if self.recent_rentals else [],
        }

