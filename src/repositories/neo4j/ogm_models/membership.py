from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipFrom

MEMBERSHIP = {"GOLD", "SILVER", "BRONZE"}

class Membership(StructuredNode):
    membershipId = IntegerProperty(unique_index=True, required=True)
    membership = StringProperty(required=True, choices=MEMBERSHIP)

    plans = RelationshipFrom('MembershipPlan', 'IS_MEMBERSHIP_TYPE')
