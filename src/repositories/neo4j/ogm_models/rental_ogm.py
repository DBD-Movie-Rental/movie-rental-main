from neomodel import StructuredNode, IntegerProperty, DateTimeProperty, StringProperty, RelationshipTo, RelationshipFrom
from .inventory_item_ogm import InventoryItem
from .employee_ogm import Employee
from .promo_code_ogm import PromoCode
from .fee_ogm import Fee
from .payment_ogm import Payment


RENTAL_STATUSES = (
    ("RESERVED", "RESERVED"),
    ("OPEN", "OPEN"),
    ("RETURNED", "RETURNED"),
    ("LATE", "LATE"),
    ("CANCELLED", "CANCELLED"),
)


class Rental(StructuredNode):
    rentalId = IntegerProperty(unique_index=True, required=True)
    rentedAtDatetime = DateTimeProperty()
    returnedAtDatetime = DateTimeProperty()
    dueAtDatetime = DateTimeProperty()
    reservedAtDatetime = DateTimeProperty()
    status = StringProperty(required=True, choices=RENTAL_STATUSES)

    # Use fully qualified string target to avoid circular import and ensure resolution
    customer = RelationshipFrom('src.repositories.neo4j.ogm_models.customer_ogm.Customer', 'RENTED')
    items = RelationshipTo(InventoryItem, 'HAS_ITEM')
    employee = RelationshipTo(Employee, 'PROCESSED_BY')
    promo = RelationshipTo(PromoCode, 'USED_PROMO')
    fees = RelationshipTo(Fee, 'HAS_FEE')
    payments = RelationshipFrom(Payment, 'FOR_RENTAL')
