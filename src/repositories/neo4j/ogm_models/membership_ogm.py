from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipFrom

# neomodel expects `choices` to be convertible to a dict via dict(choices).
# Use sequence of (value, label) pairs.
MEMBERSHIP = (
    ("GOLD", "GOLD"),
    ("SILVER", "SILVER"),
    ("BRONZE", "BRONZE"),
)

class Membership(StructuredNode):
    membershipId = IntegerProperty(unique_index=True, required=True)
    membership = StringProperty(required=True, choices=MEMBERSHIP)

    plans = RelationshipFrom('MembershipPlan', 'IS_MEMBERSHIP_TYPE')
