from neomodel import StructuredNode, IntegerProperty, FloatProperty, DateTimeProperty, RelationshipTo, RelationshipFrom
from .rental_ogm import Rental
from .customer_ogm import Customer


class Payment(StructuredNode):
    paymentId = IntegerProperty(unique_index=True, required=True)
    amountDkk = FloatProperty(required=True)
    createdAt = DateTimeProperty(required=True)
   
    rental = RelationshipTo(Rental, 'FOR_RENTAL')
    customer = RelationshipFrom(Customer, 'MADE_PAYMENT')
