from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipFrom
from .customer_ogm import Customer


class Address(StructuredNode):
    addressId = IntegerProperty(unique_index=True, required=True)
    address = StringProperty(required=True)
    city = StringProperty(required=True)
    postCode = StringProperty(required=True)
    
    customer = RelationshipFrom(Customer, 'HAS_ADDRESS')
