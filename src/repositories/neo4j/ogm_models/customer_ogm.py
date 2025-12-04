from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, RelationshipTo


class Customer(StructuredNode):
    customerId = IntegerProperty(unique_index=True, required=True)
    firstName = StringProperty(required=True)
    lastName = StringProperty(required=True)
    email = StringProperty(required=True)
    phoneNumber = StringProperty(required=True)
    createdAt = DateTimeProperty(required=True)

    addresses = RelationshipTo('Address', 'HAS_ADDRESS')
    rentals = RelationshipTo('Rental', 'RENTED')
    payments = RelationshipTo('Payment', 'MADE_PAYMENT')
