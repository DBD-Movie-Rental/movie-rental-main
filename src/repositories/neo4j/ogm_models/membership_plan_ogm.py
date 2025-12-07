from neomodel import StructuredNode, IntegerProperty, FloatProperty, DateTimeProperty, RelationshipTo
from .membership_ogm import Membership
from .customer_ogm import Customer


class MembershipPlan(StructuredNode):
    membershipPlanId = IntegerProperty(unique_index=True, required=True)
    monthlyCost = FloatProperty(required=True)
    startsOn = DateTimeProperty(required=True)
    endsOn = DateTimeProperty(required=True)
   
    membership = RelationshipTo(Membership, 'IS_MEMBERSHIP_TYPE')
    customer = RelationshipTo(Customer, 'HAS_MEMBERSHIP')
