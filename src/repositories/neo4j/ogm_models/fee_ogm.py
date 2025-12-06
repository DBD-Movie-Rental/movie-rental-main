from neomodel import StructuredNode, IntegerProperty, FloatProperty, StringProperty, RelationshipFrom


FEE_TYPES = (
    ("LATE", "LATE"),
    ("DAMAGED", "DAMAGED"),
    ("OTHER", "OTHER"),
)


class Fee(StructuredNode):
    feeId = IntegerProperty(unique_index=True, required=True)
    feeType = StringProperty(required=True, choices=FEE_TYPES)
    amountDkk = FloatProperty(required=True)
    
    rental = RelationshipFrom('Rental', 'HAS_FEE')
