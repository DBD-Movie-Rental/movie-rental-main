from neomodel import StructuredNode, IntegerProperty, FloatProperty, DateTimeProperty, RelationshipTo, RelationshipFrom


class Payment(StructuredNode):
    paymentId = IntegerProperty(unique_index=True, required=True)
    amountDkk = FloatProperty(required=True)
    createdAt = DateTimeProperty(required=True)
   
    # Use fully qualified string targets to avoid circular imports and ensure resolution
    rental = RelationshipTo('src.repositories.neo4j.ogm_models.rental_ogm.Rental', 'FOR_RENTAL')
    customer = RelationshipFrom('src.repositories.neo4j.ogm_models.customer_ogm.Customer', 'MADE_PAYMENT')
