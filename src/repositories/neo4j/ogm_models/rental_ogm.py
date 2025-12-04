from neomodel import StructuredNode, IntegerProperty, DateTimeProperty, StringProperty, RelationshipTo, RelationshipFrom


RENTAL_STATUSES = {"RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"}


class Rental(StructuredNode):
    rentalId = IntegerProperty(unique_index=True, required=True)
    rentedAtDatetime = DateTimeProperty()
    returnedAtDatetime = DateTimeProperty()
    dueAtDatetime = DateTimeProperty()
    reservedAtDatetime = DateTimeProperty()
    status = StringProperty(required=True, choices=RENTAL_STATUSES)

    customer = RelationshipFrom('Customer', 'RENTED')
    items = RelationshipTo('InventoryItem', 'HAS_ITEM')
    employee = RelationshipTo('Employee', 'PROCESSED_BY')
    promo = RelationshipTo('PromoCode', 'USED_PROMO')
    fees = RelationshipTo('Fee', 'HAS_FEE')
    payments = RelationshipFrom('Payment', 'FOR_RENTAL')
