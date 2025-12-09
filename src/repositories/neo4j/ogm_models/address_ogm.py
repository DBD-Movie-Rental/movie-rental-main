from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipFrom


class Address(StructuredNode):
    addressId = IntegerProperty(unique_index=True, required=True)
    address = StringProperty(required=True)
    city = StringProperty(required=True)
    postCode = StringProperty(required=True)

    # Use fully qualified string target to avoid circular import and ensure resolution
    customer = RelationshipFrom('src.repositories.neo4j.ogm_models.customer_ogm.Customer', 'HAS_ADDRESS')
