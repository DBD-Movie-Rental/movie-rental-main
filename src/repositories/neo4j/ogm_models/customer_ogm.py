from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, RelationshipTo


class Customer(StructuredNode):
    customerId = IntegerProperty(unique_index=True, required=True)
    firstName = StringProperty(required=True)
    lastName = StringProperty(required=True)
    email = StringProperty(required=True)
    phoneNumber = StringProperty(required=True)
    createdAt = DateTimeProperty(default_now=True)

    # Use fully qualified string targets to avoid circular imports and ensure resolution
    addresses = RelationshipTo('src.repositories.neo4j.ogm_models.address_ogm.Address', 'HAS_ADDRESS')
    rentals = RelationshipTo('src.repositories.neo4j.ogm_models.rental_ogm.Rental', 'RENTED')
    payments = RelationshipTo('src.repositories.neo4j.ogm_models.payment_ogm.Payment', 'MADE_PAYMENT')
